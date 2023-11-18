import { Subtitle, Title } from "#src/components"
import {
  RegistrationSearchResult,
  useRegistrationAPI,
} from "#src/features/registration"
import { Input } from "#src/features/registration/components/search/Input"
import { Results } from "#src/features/registration/components/search/Results"
import {
  ResultStore,
  SearchStore,
} from "#src/features/registration/stores/search"
import { Group, Skeleton, Text } from "@mantine/core"
import { action, observable, reaction } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ChangeEvent, useCallback, useEffect, useState } from "react"

export const SearchPage = () => {
  return (
    <Title title="Registrations">
      <Subtitle subtitle="Search registrations">
        <Search eventId="test" />
      </Subtitle>
    </Title>
  )
}

const Search = observer(({ eventId }: { eventId: string }) => {
  const api = useRegistrationAPI()
  const state = useLocalObservable(() => new SearchStore(api, eventId))
  const query = useLocalObservable(() => observable.box(""))

  const handleChange = useCallback(
    action((e: ChangeEvent<HTMLInputElement>) => {
      query.set(e.target.value)
    }),
    [],
  )

  useEffect(() => {
    return reaction(
      () => query.get(),
      (query) => state.search(query),
      {
        delay: 500,
      },
    )
  }, [])

  let content

  if (state.curResults) {
    if (state.curResults.ready) {
      content = <Results results={getResults(state.curResults.value)} />
    } else {
      content = <Placeholder />
    }
  } else {
    content = <NoResults />
  }

  return (
    <>
      <Input value={query.get()} onChange={handleChange} />
      {content}
    </>
  )
})

const getResults = (results: ResultStore): RegistrationSearchResult[][] => {
  const res = []
  let cur: ResultStore | undefined = results
  while (cur) {
    res.push(cur.registrations)
    cur = cur.next?.ready ? cur.next.value : undefined
  }
  return res
}

const NoResults = () => (
  <Text display="block" m="auto" c="dimmed" fz="small">
    No results
  </Text>
)

const Placeholder = () => <Skeleton h="20rem" />
