"""
LLM: factual answer from HuggingFace, optional polish via Groq.
Uses config and logging; propagates failures instead of silent fallbacks.
Supports multiple providers (HF, Groq, OpenAI, Local) for flexibility.
"""
from __future__ import annotations

import logging
from typing import List



import os
import openai
from groq import Groq
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

LLM_PROVIDERS = ["groq", "openai", "hf", "local"]
GROQ_MODELS = [
    "mixtral-8x7b-32768",  # Supported as of Jan 2026
    "llama2-70b-4096",     # Example, update as needed
]
OPENAI_MODELS = [
    "gpt-4-1106-preview",
    "gpt-3.5-turbo",
]
HF_CHAT_MODELS = [
    "meta-llama/Llama-2-70b-chat-hf",
    "HuggingFaceH4/zephyr-7b-beta",
]
HF_TEXT_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",
]
LOCAL_MODELS = []

class LLMService:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.llm_model = os.getenv("LLM_MODEL")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.hf_client = InferenceClient(api_key=self.hf_api_key) if self.hf_api_key else None
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None

    # Returns ordered list of fallback model names for the given provider
    def _get_fallbacks(self, provider: str) -> list:
        if provider == "groq":
            return GROQ_MODELS
        if provider == "openai":
            return OPENAI_MODELS
        if provider == "hf":
            return HF_CHAT_MODELS + HF_TEXT_MODELS
        if provider == "local":
            return LOCAL_MODELS
        return []

    def _try_groq(self, messages):
        # Iterates configured GROQ_MODELS until one succeeds or all fail
        if not self.groq_client:
            logger.warning("Groq API key not configured.")
            return None
        for model in ([self.llm_model] if self.llm_model else GROQ_MODELS):
            if not model:
                continue
            try:
                from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
                groq_msgs = [
                    ChatCompletionSystemMessageParam(**messages[0]),
                    ChatCompletionUserMessageParam(**messages[1])
                ]
                response = self.groq_client.chat.completions.create(
                    model=model,
                    messages=groq_msgs,
                    max_tokens=500,
                    temperature=0.1
                )
                logger.info(f"Groq LLM success with model: {model}")
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"Groq model {model} failed: {e}")
        return None

    def _try_openai(self, messages):
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured.")
            return None
        openai.api_key = self.openai_api_key
        for model in ([self.llm_model] if self.llm_model else OPENAI_MODELS):
            if not model:
                continue
            try:
                # For OpenAI Python SDK v1.x (2024+), use openai.chat.completions.create
                response = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.1
                )
                logger.info(f"OpenAI LLM success with model: {model}")
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"OpenAI model {model} failed: {e}")
        return None

    def _try_hf(self, messages):
        if not self.hf_client:
            logger.warning("HuggingFace API key not configured.")
            return None
        for model in ([self.llm_model] if self.llm_model else HF_CHAT_MODELS + HF_TEXT_MODELS):
            if not model:
                continue
            try:
                if "chat" in model or "zephyr" in model or "llama" in model:
                    response = self.hf_client.chat_completion(
                        messages=messages,
                        model=model,
                        max_tokens=500,
                        temperature=0.1
                    )
                    logger.info(f"HuggingFace chat LLM success with model: {model}")
                    return response.choices[0].message.content or ""
                else:
                    prompt = f"{messages[0]['content']}\n{messages[1]['content']}"
                    result = self.hf_client.text_generation(
                        prompt,
                        model=model,
                        max_new_tokens=500,
                        temperature=0.1,
                    )
                    logger.info(f"HuggingFace text LLM success with model: {model}")
                    return result
            except Exception as e:
                logger.warning(f"HuggingFace model {model} failed: {e}")
        return None

    def _try_local(self, messages):
        # Placeholder — extend this to integrate Ollama or other local runtimes
        logger.warning("No local LLM integration implemented.")
        return None

    def _system_messages(self, question: str, context: str):
        # Builds the system + user message list consumed by all provider clients
        return [
            {
                "role": "system",
                "content": "You are a precise and helpful AI assistant. Answer the question based ONLY on the provided context. If the answer is not in the context, say 'I cannot answer this based on the provided documents.'"
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]

    def generate_answer(self, question: str, context: str):
        # Tries the configured provider first, then falls back to the others in order
        messages = self._system_messages(question, context)
        for provider in [self.llm_provider] + [p for p in LLM_PROVIDERS if p != self.llm_provider]:
            if provider == "groq":
                answer = self._try_groq(messages)
            elif provider == "openai":
                answer = self._try_openai(messages)
            elif provider == "hf":
                answer = self._try_hf(messages)
            elif provider == "local":
                answer = self._try_local(messages)
            else:
                continue
            if answer:
                return {"answer": answer, "error": None, "fallback_used": provider != self.llm_provider}
        logger.error("All LLM providers failed.")
        return {"answer": None, "error": "All LLM providers failed.", "fallback_used": True}
