# The Interview Process

Because each interview has a list of steps, it may be tempting to think that the user
will see those steps happen in that order.

Each _step object_ defined in the interview is processed in the order it is written, but
**all steps are processed every time the state is updated**. This means a user may
experience an interview in a different order than the steps are written.

Consider this interview:

```yaml
- id: example
  questions:
    - id: q1
    - id: q2
    - id: q3
  steps:
    - ask: q1
      when: foo is defined

    - ask: q2

    - set: foo
      value: "'bar'"

    - ask: q3
```

As written, one might think the user will be asked _q2_ then _q3_, with _q1_ skipped.
But the actual order will be _q2_, _q1_, _q3_. Here's what happens:

1. `ask: q1` is processed. `foo` is not defined, so this step is skipped.
2. `ask: q2` is processed and returns a question to the user.
3. The user submits the response.
4. `ask: q1` is processed again. `foo` is not defined, so it is skipped.
5. `ask: q2` is processed. _q2_ was already asked, so it is skipped.
6. `set: foo` is processed. The state is updated and the steps are re-run again.
7. `ask: q1` is processed. `foo` is now defined, so it is executed and the user is
   finally asked _q1_.
8. The user submits the response.
9. `ask: q1` and `ask: q2` are skipped since they have already been asked.
10. `set: foo` is skipped because `foo` is already defined.
11. `ask: q3` is processed and the user is asked _q3_.

If that seems confusing, don't worry. You don't have to think too much about the order
of the interview, the system will figure that out for you.
