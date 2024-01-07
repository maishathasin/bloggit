
# Blog Git
A minimal static site generator for your Github repos


# GitBlog: Static Site Generator

[![GitHub issues](https://img.shields.io/github/issues/YourUsername/YourRepository)](https://github.com/YourUsername/YourRepository/issues)
[![GitHub forks](https://img.shields.io/github/forks/YourUsername/YourRepository)](https://github.com/YourUsername/YourRepository/network)
[![GitHub stars](https://img.shields.io/github/stars/YourUsername/YourRepository)](https://github.com/YourUsername/YourRepository/stargazers)
[![GitHub license](https://img.shields.io/github/license/YourUsername/YourRepository)](https://github.com/YourUsername/YourRepository/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)]()

GitBlog is a command-line static site generator that allows users to create personal blogs from their GitHub repositories. It fetches repository information and converts it into a static HTML site and designed with tailwindCSS.

[![bloggit](bloggit.png)]()




## Installation

```bash
```


## Usage 
```
# To build the static site from content
bloggit build

# To add a repository to the blog
bloggit add <repository_name>

# To add all repositories to the blog
bloggit addall

# To delete a specific blog
bloggit delete <blog_name>

# To show a list of all articles
bloggit show

# To open the generated site in a web browser
bloggit open
```


## Features 

- Easy-to-use command-line interface.
- Integrates with GitHub to fetch repository data.
- Generates a static HTML site that can be hosted anywhere.
- Each repo is it's own HTML file (output/contents folder) so it can be easily customizable.

