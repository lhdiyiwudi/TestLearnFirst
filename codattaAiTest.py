import asyncio
import aiohttp
import time
import json
from aiohttp import ClientSession
from typing import Dict, Any, List
import logging

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestConfig:
    """测试配置参数"""
    URL = "https://app-test.b18a.io/api/v2/frontier/task/submit"
    CONCURRENCY = 10  # 并发请求数
    TOTAL_REQUESTS = 50  # 总请求次数
    REQUEST_DELAY = 0.05  # 请求间隔(秒)
    TIMEOUT = 20  # 单次请求超时时间(秒)

    # 请求头参数（与curl指令一致）
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "origin": "https://app-test.b18a.io",
        "priority": "u=1, i",
        "referer": "https://app-test.b18a.io/frontier/project/SPEECH_TPL_000001/7443101782700100986",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWNrZXRfaWQiOiI0ZjA2MGQxNDczNGVjNmRmIiwidG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKMWMyVnlYMmxrSWpvaU5qSXhNek00TXpZek9UZ3dNREV3TmpJME9DSXNJbXh2WjJsdVgzUnBiV1VpT2pFM05EY3dNelEwT0RJdU5EZ3hOekF6ZlEuancxNmsySThvdVBERElUUG9VLU5Vb1UzSUNYXzNCR0VoYnNFUERqRUx2ZyJ9.XoMLhQDtXc3Pv48dnsLcbfPhDBhvrsxez2J6gGul2zo",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }

    # 请求体参数（与curl指令一致）
    PAYLOAD = {
        "task_id": "7443101782700100986",
        "data_submission": {
            "taskId": "7443101782700100986",
            "templateId": "SPEECH_TPL_000001",
            "data": {
                "language": "zh",
                "speech_audio": [
                    {
                        "uid": "rc-upload-1749108603444-2",
                        "url": "https://file.b18a.io/6213383639800106248_501410_.m4a",
                        "name": "录音 (11).m4a"
                    }
                ],
                "speech_text": "这是关于某某的演讲"
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
        """记录成功请求"""
        self.success_count += 1
        self.response_times.append(time_cost)
        logger.info(f"响应内容: {response_body}")

    def record_failure(self, error_msg: str, response_body: str = None) -> None:
        """记录失败请求"""
        self.failure_count += 1
        self.errors.append(error_msg)
        if response_body:
            logger.error(f"响应内容: {response_body}")


async def send_request(session: ClientSession, result: TestResult) -> None:
    """发送单个API请求并记录结果"""
    try:
        start_time = time.time()
        async with session.post(
                TestConfig.URL,
                headers=TestConfig.HEADERS,
                json=TestConfig.PAYLOAD,
                timeout=TestConfig.TIMEOUT
        ) as response:
            end_time = time.time()
            time_cost = end_time - start_time

            # 读取响应内容
            response_body = await response.text()

            # 处理响应
            if response.status == 200:
                result.record_success(time_cost, response_body)
                logger.info(f"[成功] 状态码: {response.status} | 耗时: {time_cost:.2f}s")
            else:
                error_msg = f"[失败] 状态码: {response.status}"
                result.record_failure(error_msg, response_body)
                logger.error(error_msg)

    except aiohttp.ClientError as e:
        error_msg = f"[客户端异常] {str(e)}"
        result.record_failure(error_msg)
        logger.error(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"[JSON解析失败] {str(e)}"
        result.record_failure(error_msg)
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"[未知错误] {str(e)}"
        result.record_failure(error_msg)
        logger.error(error_msg)


async def run_concurrent_test() -> Dict[str, Any]:
    """执行并发测试主流程"""
    result = TestResult()
    semaphore = asyncio.Semaphore(TestConfig.CONCURRENCY)  # 并发数控制

    async with ClientSession() as session:
        tasks = []
        for req_id in range(TestConfig.TOTAL_REQUESTS):
            if req_id > 0 and req_id % TestConfig.CONCURRENCY == 0:
                await asyncio.sleep(TestConfig.REQUEST_DELAY)

            async with semaphore:
                task = asyncio.create_task(send_request(session, result))
                tasks.append(task)

        await asyncio.gather(*tasks)

    return result.get_summary()


async def main() -> None:
    """主函数"""
    logger.info(f"开始并发测试 | 目标: {TestConfig.URL}")
    logger.info(f"配置: 并发数={TestConfig.CONCURRENCY}, 总请求数={TestConfig.TOTAL_REQUESTS}")

    start_time = time.time()
    summary = await run_concurrent_test()
    total_time = time.time() - start_time

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