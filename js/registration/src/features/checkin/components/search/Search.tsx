import { QueueItem } from "#src/features/checkin/types"
import { RegistrationSearchResult } from "#src/features/registration"
import {
  ActionIcon,
  Anchor,
  Grid,
  Table,
  Text,
  TextInput,
  Title,
} from "@mantine/core"
import { IconSearch, IconTrash } from "@tabler/icons-react"

export type SearchProps = {
  query?: string
  onChange?: (query: string) => void
  registrations?: RegistrationSearchResult[]
  nextInLine?: QueueItem[]
  onSelect?: (id: string) => void
  onSelectNextInLine?: (item: QueueItem) => void
  onRemoveNextInLine?: (item: QueueItem) => void
}

export const Search = (props: SearchProps) => {
  const {
    query,
    onChange,
    registrations,
    onSelect,
    nextInLine,
    onSelectNextInLine,
    onRemoveNextInLine,
  } = props

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
      {nextInLine && nextInLine.length > 0 && (
        <Grid.Col>
          <Title order={5}>Next In Line</Title>
          <NextInLineResults
            items={nextInLine}
            onSelect={onSelectNextInLine}
            onRemove={onRemoveNextInLine}
          />
        </Grid.Col>
      )}
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
            <Table.Th>Name</Table.Th>
            <Table.Th>Email</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {registrations.map((r) => (
            <Table.Tr key={r.id} onClick={() => onSelect && onSelect(r.id)}>
              <Table.Td>
                <Anchor
                  component="button"
                  className="CheckinSearchResults-button"
                >
                  {r.first_name}
                  {r.preferred_name
                    ? " (" + r.preferred_name + ")"
                    : undefined}{" "}
                  {r.last_name}
                </Anchor>
              </Table.Td>
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

export type NextInLineResultsProps = {
  items?: QueueItem[]
  onSelect?: (item: QueueItem) => void
  onRemove?: (item: QueueItem) => void
}

export const NextInLineResults = (props: NextInLineResultsProps) => {
  const { items, onSelect, onRemove } = props

  let content

  if (!items) {
    content = null
  } else if (items.length > 0) {
    content = (
      <Table highlightOnHover striped>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Email</Table.Th>
            <Table.Th className="CheckinSearchResults-removeColumn"></Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {items.map((item) => (
            <Table.Tr key={item.id} onClick={() => onSelect && onSelect(item)}>
              {item.registration ? (
                <>
                  <Table.Td>
                    <Anchor
                      component="button"
                      className="CheckinSearchResults-button"
                    >
                      {item.registration.first_name}
                      {item.registration.preferred_name
                        ? " (" + item.registration.preferred_name + ")"
                        : undefined}{" "}
                      {item.registration.last_name}
                    </Anchor>
                  </Table.Td>
                  <Table.Td>{item.registration.email}</Table.Td>
                  <Table.Td className="CheckinSearchResults-removeColumn">
                    <Anchor
                      component="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        onRemove && onRemove(item)
                      }}
                      variant="subtle"
                      size="sm"
                    >
                      Remove
                    </Anchor>
                  </Table.Td>
                </>
              ) : (
                <>
                  <Table.Td>
                    <Anchor
                      component="button"
                      className="CheckinSearchResults-button"
                    >
                      Unknown Person
                    </Anchor>
                  </Table.Td>
                  <Table.Td></Table.Td>
                  <Table.Td className="CheckinSearchResults-removeColumn">
                    <Anchor
                      component="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        onRemove && onRemove(item)
                      }}
                      variant="subtle"
                      size="sm"
                    >
                      Remove
                    </Anchor>
                  </Table.Td>
                </>
              )}
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
