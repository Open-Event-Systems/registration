# Concepts

Below is a summary of several concepts in the interview system.

## Questions

A _question_ is exactly what it sounds like&mdash;a question presented to the user.

A question may provide any number of input fields for the user to fill out. Ideally,
this would be maybe one or two fields to keep the question simple and focused.

A question could even have zero fields. In this case, it would simply serve to display a
message to the user before continuing.

When creating an interview, you won't always need to specify which questions are asked,
or in what order. The interview process determines that automatically based on rich
logic rules.

## Interviews

An _interview_ is a series of _steps_ taken in order to gather information from a user.
Usually these will be questions, but there are more things that may happen behind the
scenes.

## Steps

A _step_ is an action taken as part of an interview. The most obvious step is to ask a
question, but there are more steps that will be detailed later.

## State

The _interview state_ is an object that records the user's progress through an
interview. It stores their responses as well as other metadata used during the
interview.

The state is submitted along with each of the user's responses, and the user receives an
updated state along with the next step.
