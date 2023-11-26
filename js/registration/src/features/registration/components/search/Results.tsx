import { RegistrationSearchResult } from "#src/features/registration"
import { Button, Loader, Table, TableTdProps, Text } from "@mantine/core"
import { observer } from "mobx-react-lite"
import { createContext, useContext, useState } from "react"

export type ResultsProps = {
  registrations?: RegistrationSearchResult[]
  getLink?: (
    registration: RegistrationSearchResult,
  ) => [string | undefined, string | undefined] | undefined
  hasMore?: boolean
  onMore?: () => Promise<void>
}

export const Results = observer((props: ResultsProps) => {
  const { registrations = [], getLink, hasMore, onMore } = props

  const [loading, setLoading] = useState(false)

  let content

  if (registrations.length > 0) {
    content = (
      <Table highlightOnHover striped>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>No.</Table.Th>
            <Table.Th>Pref</Table.Th>
            <Table.Th>First</Table.Th>
            <Table.Th>Last</Table.Th>
            <Table.Th>Email</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <ResultRows getLink={getLink} registrations={registrations} />
        {hasMore && (
          <Table.Tfoot>
            <Table.Tr>
              <Table.Td colSpan={5}>
                {loading ? (
                  <Loader type="dots" />
                ) : (
                  <Button
                    variant="transparent"
                    onClick={() => {
                      if (!onMore) {
                        return
                      }

                      setLoading(true)
                      onMore()
                        .then(() => setLoading(false))
                        .catch((e) => {
                          setLoading(false)
                          throw e
                        })
                    }}
                  >
                    More
                  </Button>
                )}
              </Table.Td>
            </Table.Tr>
          </Table.Tfoot>
        )}
      </Table>
    )
  } else {
    content = <NoResults />
  }

  return (
    <Table.ScrollContainer
      className="RegistrationSearchResults-root"
      minWidth={500}
    >
      {content}
    </Table.ScrollContainer>
  )
})

Results.displayName = "RegistrationSearchResults"

const NoResults = () => (
  <Text className="RegistrationSearchResults-noResults" c="dimmed">
    No results
  </Text>
)

type ResultRowsProps = {
  getLink?: (
    registration: RegistrationSearchResult,
  ) => [string | undefined, string | undefined] | undefined
  registrations?: RegistrationSearchResult[]
}

const ResultRows = (props: ResultRowsProps) => {
  const { registrations = [], getLink } = props
  return (
    <Table.Tbody>
      {registrations.map((r) => (
        <Table.Tr key={r.id}>
          <LinkContext.Provider
            value={(getLink && getLink(r)) || [undefined, undefined]}
          >
            <LinkCol tab aria-label={getLabel(r)}>
              {r.number}
            </LinkCol>
            <LinkCol>{r.preferred_name}</LinkCol>
            <LinkCol>{r.first_name}</LinkCol>
            <LinkCol>{r.last_name}</LinkCol>
            <LinkCol>{r.email}</LinkCol>
          </LinkContext.Provider>
        </Table.Tr>
      ))}
    </Table.Tbody>
  )
}

const LinkContext = createContext<[string | undefined, string | undefined]>([
  undefined,
  undefined,
])

const LinkCol = (props: TableTdProps & { tab?: boolean }) => {
  const { "aria-label": ariaLabel, tab, children, ...other } = props

  const [href, target] = useContext(LinkContext)

  return (
    <Table.Td {...other}>
      {href ? (
        <a
          href={href}
          tabIndex={tab ? undefined : -1}
          target={target}
          aria-label={ariaLabel}
        >
          {children}
        </a>
      ) : (
        children
      )}
    </Table.Td>
  )
}

const getLabel = (r: RegistrationSearchResult) => {
  const names = [r.preferred_name || r.first_name, r.last_name]
    .filter((r) => !!r)
    .join(" ")
  return names || r.email || "Registration"
}
