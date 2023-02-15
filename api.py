
import re
from termcolor import colored
from news_article import NEWS_ARTICLE
from steamship import check_environment, RuntimeEnvironments, Steamship
from steamship.invocable import post, PackageService


class PromptPackage(PackageService):
  # Modify this to customize behavior to match your needs.
  PROMPT = """Act as an executive assistant and write an executive summary of a {input_type}. Write the summary as a bulleted list, separate each bullet with two new lines. Focus on the key message and skip side information. Keep each bullet short and less than 20 words by removing fluffy words. Keep your output under {max_n_tokens} tokens. 
  
  {input_type}: {text}."""

  REDUCTION_FACTOR = .05
  MIN_N_TOKENS = 50

  # When this package is deployed, this annotation tells Steamship
  # to expose an endpoint that accepts HTTP POST requests for the
  # `/generate` request path.
  # See README.md for more information about deployment.
  @post("generate")
  def generate(self, text: str) -> str:
    """Generate text from prompt parameters."""
    max_n_tokens = max(
      len(text.split()) * self.REDUCTION_FACTOR, self.MIN_N_TOKENS)

    llm_config = {
        # Controls length of generated output.
        "max_words": 500,
        # Controls randomness of output (range: 0.0-1.0).
        "temperature": 0.8
      }
    prompt_args = {
      "text": text,
      "max_n_tokens": max_n_tokens,
      "input_type": "news article"
    }

    llm = self.client.use_plugin("gpt-3", config=llm_config)
    completion = llm.generate(self.PROMPT, prompt_args)

    return re.sub(r"([\n]+)-(\w)*", r"\n\n- ", completion).strip()


# Try it out locally by running this file!
if __name__ == "__main__":
  print(colored("Generate Summaries with GPT-3\n", attrs=['bold']))

  text = NEWS_ARTICLE

  # This helper provides runtime API key prompting, etc.
  check_environment(RuntimeEnvironments.REPLIT)

  with Steamship.temporary_workspace() as client:
    prompt = PromptPackage(client)
    print(colored("Let's try it out!", 'green'))

    try_again = True
    while try_again:
      print()
      print("Going to summarize this NYT article: shorturl.at/fjDGS:")
      print("Fork this Replit if you want to summarize a different article.")
      print(colored("Generating...", 'grey'))

      # This is the prompt-based generation call
      print(colored("Summary:\n", 'grey'), f'{prompt.generate(text=text)}\n')

      try_again = input("Try again (y/n)? ").lower().strip() == 'y'

    print("Ready to share with your friends (and the world)?")
    print("Run ", colored("$ ship deploy ", color='green',
                          on_color='on_black'),
          "to get a production-ready API endpoint and web-based demo app.")
