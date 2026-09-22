from dataclasses import dataclass


class AIProviderError(Exception):
	"""Raised when an AI provider cannot produce a response."""


@dataclass
class ProviderResponse:
	content: str
	uncertainty_notice: str = "Verify important details with your course materials or a teacher."


class MockProvider:
	def generate(self, prompt):
		request = prompt.rsplit("Student request:", 1)[-1].strip()
		return ProviderResponse(
			content=(
				"Mock mode is active. I received your request:\n\n"
				f"{request}\n\n"
				"Add an AI provider key in .env when you are ready for generated answers."
			)
		)


class OpenAIProvider:
	def __init__(self, api_key, model, timeout_seconds):
		try:
			from openai import OpenAI
		except ImportError as error:
			raise AIProviderError(
				"The OpenAI package is not installed. Install project requirements first."
			) from error

		self.client = OpenAI(api_key=api_key, timeout=timeout_seconds)
		self.model = model

	def generate(self, prompt):
		try:
			response = self.client.chat.completions.create(
				model=self.model,
				messages=[
					{
						"role": "system",
						"content": "You are an accurate, supportive study assistant.",
					},
					{"role": "user", "content": prompt},
				],
			)
			content = response.choices[0].message.content
			if not content:
				raise AIProviderError("The AI provider returned an empty response.")
			return ProviderResponse(content=content)
		except AIProviderError:
			raise
		except Exception as error:
			raise AIProviderError("The AI provider is temporarily unavailable.") from error


class GeminiProvider:
	def __init__(self, api_key, model):
		try:
			from google import genai
		except ImportError as error:
			raise AIProviderError(
				"The Google GenAI package is not installed. Install project requirements first."
			) from error

		self.client = genai.Client(api_key=api_key)
		self.model = model

	def generate(self, prompt):
		try:
			response = self.client.models.generate_content(
				model=self.model,
				contents=prompt,
			)
			content = response.text
			if not content:
				raise AIProviderError("The Gemini provider returned an empty response.")
			return ProviderResponse(content=content)
		except AIProviderError:
			raise
		except Exception as error:
			if getattr(error, "status_code", None) == 401 or getattr(error, "code", None) == 401:
				raise AIProviderError(
					"Gemini authentication failed. Create a Gemini API key in Google AI Studio and update GEMINI_API_KEY."
				) from error
			if getattr(error, "status_code", None) == 503 or getattr(error, "code", None) == 503:
				raise AIProviderError(
					"Gemini is temporarily busy. Please wait a moment and try again."
				) from error
			raise AIProviderError("The Gemini provider is temporarily unavailable.") from error


def create_provider(config):
	provider_name = (config.get("AI_PROVIDER") or "mock").lower()
	if provider_name == "mock":
		return MockProvider()
	if provider_name == "openai":
		api_key = config.get("OPENAI_API_KEY")
		if not api_key:
			raise AIProviderError("OPENAI_API_KEY is not configured.")
		return OpenAIProvider(
			api_key=api_key,
			model=config.get("OPENAI_MODEL", "gpt-4o-mini"),
			timeout_seconds=config.get("AI_REQUEST_TIMEOUT_SECONDS", 30),
		)
	if provider_name == "gemini":
		api_key = config.get("GEMINI_API_KEY")
		if not api_key:
			raise AIProviderError("GEMINI_API_KEY is not configured.")
		return GeminiProvider(
			api_key=api_key,
			model=config.get("GEMINI_MODEL", "gemini-flash-lite-latest"),
		)
	raise AIProviderError(f"Unsupported AI provider: {provider_name}")