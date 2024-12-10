<p align="center"><a href="https://nitric.io" target="_blank"><img src="https://raw.githubusercontent.com/nitrictech/nitric/main/docs/assets/nitric-logo.svg" height="120"></a></p>

# Nitric AI Podcast Generator

This is the AI Podcast generator app from the [Build AI Generated Podcasts](https://www.youtube.com/watch?v=4aLqP0KHCu0&list=PL45B6z4_ZDhQTLlzvUjROk2mB_GRzgyhs&index=2) series on YouTube.

## Additional Guides

You can also follow the guide for building the app with Python in the following parts:

- [AI Podcast Part 1](https://nitric.io/docs/guides/python/ai-podcast-part-1)
- If you want to use an LLM to generate the text in the flow, follow [AI Podcast Part 2](https://nitric.io/docs/guides/python/ai-podcast-part-2)

## About Nitric

This is a [Nitric](https://nitric.io) Python project, but Nitric is a framework for rapid development of cloud-native and serverless applications in many languages.

## Learning Nitric

Nitric provides [documentation](https://nitric.io/docs) and [guides](https://nitric.io/docs/guides?langs=python) to help you get started quickly.

If can also join [Discord](https://nitric.io/chat) to chat with the community, or view the project on [GitHub](https://github.com/nitrictech/nitric).

## Running this project

To run this project you'll need the [Nitric CLI](https://nitric.io/docs/get-started/installation) installed, then you can use the CLI commands to run, build or deploy the project. You'll also need to install [uv](https://github.com/astral-sh/uv) for dependency management.

Install the dependencies:

```bash
uv sync
```

Next, start nitric services.

> This will automatically restart when you make changes to your functions

```bash
nitric start
```

You'll see your services connect in the terminal output.
