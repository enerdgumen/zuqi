import aiohttp
from box import Box
from conductor.config import trivia_fetch_size, trivia_max_fetch_tentatives


TOKEN_NOT_FOUND = 3
TOKEN_EMPTY = 3


class OpenTriviaQuizSource:
    def __init__(self, base_url='https://opentdb.com'):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        self.token = None
        self.tentative = 0
        self.questions = []

    async def next(self):
        if len(self.questions) == 0:
            self.questions = await self._fetch_questions()
        return self.questions.pop()

    async def _fetch_questions(self):
        if self.tentative > trivia_max_fetch_tentatives:
            raise RuntimeError('Too many OpenTrivia failures')
        if not self.token:
            self.token = await self._acquire_token()
        async with self.session.get(f'{self.base_url}/api.php',
                                    params=Box(amount=trivia_fetch_size, type='multiple', token=self.token)) as res:
            body = Box(await res.json())
            if body.response_code == 0:
                self.tentative = 0
                return [
                    Box(
                        question=result.question,
                        answers=[result.correct_answer] + result.incorrect_answers,
                        answer=0
                    )
                    for result in body.results
                ]
            if body.response_code == TOKEN_NOT_FOUND or body.response_code == TOKEN_EMPTY:
                self.token = None
                self.tentative += 1
                return self.next()
            raise RuntimeError(f'Unexpected OpenTrivia error: {body}')

    async def _acquire_token(self):
        async with self.session.get(f'{self.base_url}/api_token.php', params=Box(command='request')) as res:
            body = await res.json()
            return body['token']

    async def close(self):
        await self.session.close()
