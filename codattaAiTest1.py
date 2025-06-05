import asyncio
import aiohttp
import time
import json
from aiohttp import ClientSession
from typing import Dict, Any, List
import logging

# 配置日志格式，显示详细响应内容
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestConfig:
    """测试配置参数"""
    URL = "https://app-test.b18a.io/api/v2/frontier/task/submit"
    CONCURRENCY = 10          # 并发请求数
    TOTAL_REQUESTS = 50        # 总请求次数
    REQUEST_DELAY = 2        # 请求间隔(秒)，避免服务器过载
    TIMEOUT = 30               # 单次请求超时时间(秒)

    # 请求头参数（与curl指令一致）
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "origin": "https://app-test.b18a.io",
        "priority": "u=1, i",
        "referer": "https://app-test.b18a.io/frontier/project/NFT_TPL_000001/7433779456200100961",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWNrZXRfaWQiOiIzNDMxMmY3ZmY1NDc3MDE4IiwidG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKMWMyVnlYMmxrSWpvaU5qazVPVE00TWpneE9UY3dNREV3TnpBME15SXNJbXh2WjJsdVgzUnBiV1VpT2pFM05EY3hNamc1T0RBdU1EQXdORFl6ZlEuNXRxQUlnbW8xQXRBRjZhWnFwZjlZNEtDSS0wRWxGWUJ6R3AxT2IzeEt6OCJ9.PC_fQjNEJvSPOmC3sz6x9cyvn9cGz2DR1XRYPfwIVrA",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    # 请求体参数（与curl指令一致）
    PAYLOAD = {
        "task_id": "7433779456200100961",
        "data_submission": {
            "taskId": "7433779456200100961",
            "templateId": "NFT_TPL_000001",
            "data": {
                "nft_image": [
                    {
                        "uid": "rc-upload-1749109167412-17",
                        "url": "https://file.b18a.io/6999382819700107043_344872_.png",
                        "name": "屏幕截图 2025-06-04 200738.png"
                    }
                ],
                "nft_description": "阿达阿达是的"
            }
        }
    }


class TestResult:
    """测试结果统计"""

    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.response_times = []
        self.errors = []

    def record_success(self, time_cost: float, response_body: str) -> None:
        """记录成功请求及响应体"""
        self.success_count += 1
        self.response_times.append(time_cost)
        logger.info(f"响应体: {response_body}")

    def record_failure(self, error_msg: str, response_body: str) -> None:
        """记录失败请求及响应体"""
        self.failure_count += 1
        self.errors.append(f"{error_msg} | 响应体: {response_body}")

    def get_summary(self) -> Dict[str, Any]:
        """生成测试结果摘要"""
        if not self.response_times:
            avg_time = 0
            max_time = 0
            min_time = 0
        else:
            avg_time = sum(self.response_times) / len(self.response_times)
            max_time = max(self.response_times)
            min_time = min(self.response_times)

        return {
            "total_requests": self.success_count + self.failure_count,
            "success_rate": self.success_count / (self.success_count + self.failure_count) * 100
            if (self.success_count + self.failure_count) > 0 else 0,
            "avg_response_time": round(avg_time, 2),
            "max_response_time": round(max_time, 2),
            "min_response_time": round(min_time, 2),
            "error_samples": self.errors[:5]  # 最多显示5个错误样例
        }


async def send_single_request(session: ClientSession, result: TestResult) -> None:
    """发送单个API请求并记录结果"""
    try:
        start_time = time.time()
        async with session.post(
                TestConfig.URL,
                headers=TestConfig.HEADERS,
                json=TestConfig.PAYLOAD,
                timeout=aiohttp.ClientTimeout(total=TestConfig.TIMEOUT)
        ) as response:
            end_time = time.time()
            time_cost = end_time - start_time
            response_body = await response.text()  # 读取完整响应体

            # 处理响应
            if response.status == 200:
                result.record_success(time_cost, response_body)
                logger.info(f"[成功] 状态码: {response.status} | 耗时: {time_cost:.2f}s")
            else:
                error_msg = f"[失败] 状态码: {response.status}"
                result.record_failure(error_msg, response_body)
                logger.error(f"{error_msg} | 耗时: {time_cost:.2f}s")

    except aiohttp.ClientError as e:
        # 处理网络相关异常（如连接超时、DNS错误等）
        error_msg = f"[客户端异常] {str(e)}"
        result.record_failure(error_msg, "无响应体（网络异常）")
        logger.error(error_msg)
    except json.JSONDecodeError as e:
        # 处理响应解析异常
        error_msg = f"[JSON解析失败] {str(e)}"
        result.record_failure(error_msg, "响应体解析失败")
        logger.error(error_msg)
    except Exception as e:
        # 处理其他未知异常
        error_msg = f"[未知错误] {str(e)}"
        result.record_failure(error_msg, "无响应体（未知异常）")
        logger.error(error_msg)


async def run_concurrent_test() -> Dict[str, Any]:
    """执行并发测试主流程"""
    result = TestResult()
    semaphore = asyncio.Semaphore(TestConfig.CONCURRENCY)  # 并发数控制

    async with ClientSession() as session:
        tasks = []
        for req_id in range(TestConfig.TOTAL_REQUESTS):
            # 控制请求间隔，避免瞬间压力过大
            if req_id > 0 and req_id % TestConfig.CONCURRENCY == 0:
                await asyncio.sleep(TestConfig.REQUEST_DELAY)

            # 使用信号量限制并发
            async with semaphore:
                task = asyncio.create_task(send_single_request(session, result))
                tasks.append(task)

        # 等待所有请求完成
        await asyncio.gather(*tasks)

    return result.get_summary()


async def main() -> None:
    """主函数"""
    logger.info(f"开始并发测试 | 目标: {TestConfig.URL}")
    logger.info(f"配置: 并发数={TestConfig.CONCURRENCY}, 总请求数={TestConfig.TOTAL_REQUESTS}")

    start_time = time.time()
    summary = await run_concurrent_test()
    total_time = time.time() - start_time

    # 打印测试结果
    print("\n===== 并发测试结果汇总 =====")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"总请求数: {summary['total_requests']}")
    print(f"成功率: {summary['success_rate']:.2f}%")
    print(f"平均响应时间: {summary['avg_response_time']} 秒")
    print(f"最大响应时间: {summary['max_response_time']} 秒")
    print(f"最小响应时间: {summary['min_response_time']} 秒")

    if summary["error_samples"]:
        print("\n错误样例:")
        for i, error in enumerate(summary["error_samples"], 1):
            print(f"{i}. {error}")


if __name__ == "__main__":
    asyncio.run(main())