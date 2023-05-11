from steamship import RuntimeEnvironments, Steamship, check_environment
from termcolor import colored

# Evaluating bias in news articles through comparison against other sources.
def main():
    # This helper provides runtime API key prompting, etc.
    check_environment(RuntimeEnvironments.LOCALHOST)

    with Steamship.temporary_workspace() as client:
        api = client.use(package_handle="bias-compass")

        while True:
            article_link = input(colored("Article: ", "blue"))
            print(colored("Please be patient. Finding Articles...", "blue"), flush=True)
            response = api.invoke("/evaluate_article", article_link=article_link)
            print(colored("Articles: ", "blue"), colored(f'{response["output"].strip()}', "green"))
            print("\n")

if __name__ == "__main__":
    main()