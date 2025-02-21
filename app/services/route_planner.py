import openai


class RoutePlannerLLM:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.conversation_history = []

    def get_response(self, prompt) -> str:
        self.conversation_history.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", messages=self.conversation_history
            )

            assistant_response = response.choices[0].message.content

            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )

            return assistant_response

        except Exception as e:
            print(f"Error: {e}")
            return None
