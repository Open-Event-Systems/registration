import { RegistrationSearchResult } from "#src/features/registration"
import {
  Input,
  InputProps,
} from "#src/features/registration/components/search/Input"
import {
  Results,
  ResultsProps,
} from "#src/features/registration/components/search/Results"

export type SearchProps = {
  events?: { id: string; name: string }[]
  registrations?: RegistrationSearchResult[]
  hasMore?: boolean
  onMore?: () => Promise<void>
  getLink?: (
    registration: RegistrationSearchResult,
  ) => [string | undefined, string | undefined] | undefined
  InputProps?: Partial<InputProps>
  ResultsProps?: Partial<ResultsProps>
}

export const Search = (props: SearchProps) => {
  const {
    events,
    registrations,
    getLink,
    hasMore,
    onMore,
    InputProps,
    ResultsProps,
  } = props
  return (
    <>
      <Input
        {...InputProps}
        SelectProps={{
          data: events && events.map((e) => ({ value: e.id, label: e.name })),
          ...InputProps?.SelectProps,
        }}
      />
      <Results
        registrations={registrations}
        getLink={getLink}
        {...ResultsProps}
        hasMore={hasMore}
        onMore={onMore}
      />
    </>
  )
}
