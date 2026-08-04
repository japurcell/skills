URL Source: <https://www.thoughtworks.com/en-us/insights/blog/engineering-effectiveness/elevate-developer-experiences-cli-design-guidelines>

---

description: CLI design guidelines can be incredibly beneficial for developer productivity. Learn more on the blog.
title: Elevate developer experiences with CLI design guidelines

---

# Elevate developer experiences with CLI design guidelines

By

Jacob Bo Tiedemann

Published: November 09, 2023

In the craft of software development, the command-line interface (CLI) stands as a true companion of every developer: efficient, precise and wielding the power to orchestrate complex operations. At the intersection of functionality and usability lies the essence of CLI design — an often underestimated facet that can make or break a developer's workflow.

On our journey to build a [developer experience platform](https://www.thoughtworks.com/about-us/events/developer-experience-platforms), we recognized the profound impact of CLI design on the developer experience. We funneled our research and learnings into a set of design guidelines with the aim to craft interfaces that are not just efficient, but intuitive. We believe that a well-crafted CLI should be an extension of a developer's thought process, seamlessly fitting into their flows.

We’d like to share our eight design guidelines as a starting point and exemplar for those who, like us, endeavor to build CLIs that resonate with developers. As all design guidelines they are recommendations to be judged and adopted on a case-by-case basis by the individuals implementing them.

## Be consistent in structure and follow common naming

Stick to common industry patterns.That way, our users are much more likely to find it intuitive. Don’t use --ver when you can use -v and --verbose. Custom deviations are just surprises; they only lead to confusion.

- Stick to the command structure _platform-cli \[noun\] \[verb\]_

- Use kebab-case for command and flags

## Prompt if you can, but never mandate them

Accepting input as a prompt is desirable to guide first-time users or users who return after a longer time period. However, you should never require a prompt. Users need to be able to use your CLI for automation. Always allow them to override prompts.

- Use prompts for confirmation for critical actions or to deliberately guide the user
- Provide complementary flags for prompts
- Provide a force flag to enable scripting _(-f, --force)_

- Offer defaults to just continue with Enter

## Use expressive flags

Prioritizing clarity over fast typing means prioritizing flags over arguments. Option names should be human-readable and supplemented by short aliases (e.g. _\-v_ for _\--verbose_).

- A rule of thumb is one argument is fine, two are questionable, and three is an absolute no

- Avoid fixed positions for options. Getting disrupted by a wrong order is simply annoying

## Avoid implicit steps

Every action taken by a command should be transparent to the user. Implicit steps are dangerous and damage the quality of the developer experience. Think, for example, of an init command that overrides existing configuration without informing or asking the user.

- Always provide information on implicit steps or avoid them by splitting the command

## Always provide help

For those moments when our users can’t figure out how to proceed, it’s important to provide easily accessible help, directly at the touchpoint. Provide descriptions of the command, arguments and flags. The examples of common usage section is by far the most read and revisited by developers.

## Output informative error messages

Given the nature of CLIs, errors are commonplace. Without a graphical user interface, we only can guide the user by displaying an error message; it’s a default behavior of a CLI. This is why you need to make your error messages descriptive and informative.

- Exit with nonzero status code if and only if the program terminated with errors
- Write to stdout for information and warnings, stderr for errors
- Provide error messages that are informative, including error code, title, description, resolution steps, and URL for further assistance

###

## Keep the user in the loop and indicate progress

Keep users informed and do not let them hang in long periods of uncertainty.

- Output the current step’s information
- If commands take a little longer to run, indicate to the user that it is still running
- Leverage OS notifications when a very long-running task is done

###

## Be fun and fancy

A CLI does not have to be dull black-and-white text. Make a developer’s day with some ASCII-ART or emoji. Check out [12 Factor CLI Apps by Jeff D.](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46) for more inspiration.

- Highlight important information with color
- Indicate progress with spinners and progress bars
- Structure information in tables
- Keep the output machine-readable to enable automation

Get more inspiration from the sources used in this article and further readings:

- [12 Factor CLI Apps by Jeff D.](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)
- [Designing CLI Tools by Emily Goldfein](https://medium.com/@emilygoldfein/designing-cli-tools-a8e0858f606e)
- [Exploring CLI Best Practices by Kevin Deisz](https://eng.localytics.com/exploring-cli-best-practices/)
- [UX for Command Line Tools by Amodu Temitope](https://blog.prototypr.io/ux-for-command-line-tools-4630eb0b3c9b)
- [Heroku’s CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide)
- [Exploring CLI best practices by Kevin Newton](https://kddnewton.com/2016/10/11/exploring-cli-best-practices.html)

Disclaimer: The statements and opinions expressed in this article are those of the author(s) and do not necessarily reflect the positions of Thoughtworks.
