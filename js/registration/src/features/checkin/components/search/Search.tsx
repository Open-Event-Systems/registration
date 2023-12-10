import { RegistrationSearchResult } from "#src/features/registration"
import { Grid, Table, Text, TextInput } from "@mantine/core"
import { IconSearch } from "@tabler/icons-react"

export type SearchProps = {
  query?: string
  onChange?: (query: string) => void
  registrations?: RegistrationSearchResult[]
  onSelect?: (id: string) => void
}

export const Search = (props: SearchProps) => {
  const { query, onChange, registrations, onSelect } = props

  return (
    <Grid>
      <Grid.Col>
        <TextInput
          autoFocus
          title="Search"
          placeholder="Search"
          leftSection={<IconSearch />}
          value={query}
          onChange={(e) => {
            onChange && onChange(e.target.value)
          }}
        />
      </Grid.Col>
      <Grid.Col>
        <Results registrations={registrations} onSelect={onSelect} />
      </Grid.Col>
    </Grid>
  )
}

export type ResultsProps = {
  registrations?: RegistrationSearchResult[]
  onSelect?: (id: string) => void
}

export const Results = (props: ResultsProps) => {
  const { registrations, onSelect } = props

  let content

  if (!registrations) {
    content = null
  } else if (registrations.length > 0) {
    content = (
      <Table highlightOnHover striped>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>First (Pref)</Table.Th>
            <Table.Th>Last</Table.Th>
            <Table.Th>Email</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {registrations.map((r) => (
            <Table.Tr key={r.id} onClick={() => onSelect && onSelect(r.id)}>
              <Table.Td>
                {r.first_name}
                {r.preferred_name ? " (" + r.preferred_name + ")" : undefined}
              </Table.Td>
              <Table.Td>{r.last_name}</Table.Td>
              <Table.Td>{r.email}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    )
  } else {
    content = <NoResults />
  }

  return (
    <Table.ScrollContainer className="CheckinSearchResults-root" minWidth={500}>
      {content}
    </Table.ScrollContainer>
  )
}

const NoResults = () => (
  <Text className="CheckinSearchResults-noResults" c="dimmed">
    No results
  </Text>
)
