import { RegistrationSearchResult } from "#src/features/registration"
import { Button, Loader, Table, TableTdProps } from "@mantine/core"
import { createContext, useContext, useState } from "react"

export type ResultsProps = {
  results: RegistrationSearchResult[][]
  getLink?: (
    registration: RegistrationSearchResult,
  ) => [string | undefined, string | undefined] | undefined
  onMore?: () => Promise<void>
}

export const Results = (props: ResultsProps) => {
  const { results, getLink, onMore } = props

  const [loading, setLoading] = useState(false)

  return (
    <Table highlightOnHover striped className="RegistrationSearchResults-root">
      <Table.Thead>
        <Table.Tr>
          <Table.Th>No.</Table.Th>
          <Table.Th>Pref</Table.Th>
          <Table.Th>First</Table.Th>
          <Table.Th>Last</Table.Th>
          <Table.Th>Email</Table.Th>
        </Table.Tr>
      </Table.Thead>
      {results.map((registrations, i) => (
        <ResultSet
          key={registrations[0]?.id ?? i}
          registrations={registrations}
          getLink={getLink}
        />
      ))}
      {onMore && (
        <Table.Tfoot>
          <Table.Tr>
            <Table.Td colSpan={5}>
              {loading ? (
                <Loader type="dots" />
              ) : (
                <Button
                  variant="transparent"
                  onClick={() => {
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
}

type ResultSetProps = {
  getLink?: (
    registration: RegistrationSearchResult,
  ) => [string | undefined, string | undefined] | undefined
  registrations: RegistrationSearchResult[]
}

const ResultSet = (props: ResultSetProps) => {
  const { registrations, getLink } = props
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
