from steamship import RuntimeEnvironments, Steamship, check_environment
from termcolor import colored


def main():
    # This helper provides runtime API key prompting, etc.
    check_environment(RuntimeEnvironments.LOCALHOST)

    with Steamship.temporary_workspace() as client:
        api = client.use(package_handle="bias-compass")

        while True:
            query = input(colored("Query: ", "blue"))
            print(colored("Please be patient. Generating...", "blue"), flush=True)
            response = api.invoke("/evaluate_article", query=query)
            print(colored("Answer: ", "blue"), colored(f'{response["output"].strip()}', "green"))
            print()
            print(colored("Intermediate Steps: ", "blue"))
            step = 1
            for action in response["intermediate_steps"]:
                print(
                    colored(
                        f"{step}. Tool({action[0].get('tool', 'unknown')}): {action[0].get('tool_input', 'unknown')}",
                        "blue",
                    ),
                    colored(f"{action[1]}", "green"),
                )
                step = step + 1
            print("\n-----\n")


if __name__ == "__main__":
    main()