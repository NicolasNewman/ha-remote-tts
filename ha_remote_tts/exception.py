from typing import Optional, Any


class ApiError(Exception):
	status_code: Optional[int]
	body: Any

	def __init__(self, *, status_code: Optional[int] = None, body: Any = None):
		self.status_code = status_code
		self.body = body

	def __str__(self) -> str:
		return f'status_code: {self.status_code}, body: {self.body}'
