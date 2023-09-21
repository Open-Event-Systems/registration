# Introduction

This software provides the server-side library and service for a guided interview
system. It allows you to collect information from users via a series of simple questions
instead of a single form.

An interview has several advantages over a traditional form:

- No matter how straightforward a form might seem, users will still manage to make
  mistakes. The interview format breaks the form down into smaller segments, allowing
  the user to focus on one step at a time.

- Complicated information can be gathered from the user by asking simple, easy to
  understand questions and deriving the information from their answers.

  Example: instead of asking "Is your child a _qualifying child_ for the Earned Income
  Tax Credit (EITC)?" you might ask:

  - "What is your child's date of birth?"
  - "Is your child a full time student?"
  - "Is your child disabled?"

  and use those answers to determine the answer.

- The interview can include different questions based on the user's answers to previous
  questions. This allows the user to skip steps that are not relevant.

  In the previous example, if the child's birth date reveals that they are young enough
  to qualify, the following questions about their student status or disability can be
  automatically skipped.

This project is heavily inspired by [docassemble](https://docassemble.org/). The goal is
to provide similar functionality as a lightweight, extensible, and easier to integrate
system.
