import {
  CheckoutListResponse,
  CheckoutState,
} from "#src/features/checkout/types/Checkout"
import {
  ActionIcon,
  Box,
  Checkbox,
  Group,
  Table,
  Text,
  TextInput,
} from "@mantine/core"
import { IconSearch, IconShoppingCartShare } from "@tabler/icons-react"
import { ReactNode } from "react"

export type SearchProps = SearchInputProps & SearchResultsProps

export const Search = (props: SearchProps) => {
  const { value, showAll, onChange, results, onSelect, getLink } = props

  return (
    <Search.Root>
      <Search.Input value={value} showAll={showAll} onChange={onChange} />
      <Search.Results results={results} onSelect={onSelect} getLink={getLink} />
    </Search.Root>
  )
}

const Root = ({ children }: { children?: ReactNode }) => {
  return <Box className="CheckoutSearch-root">{children}</Box>
}

Search.Root = Root

export type SearchInputProps = {
  value?: string
  showAll?: boolean
  onChange?: (value: { query: string; showAll: boolean }) => void
}

const Input = (props: SearchInputProps) => {
  const { value, showAll, onChange } = props

  return (
    <Group className="CheckoutSearch-inputGroup">
      <TextInput
        className="CheckoutSearch-query"
        leftSection={<IconSearch />}
        value={value}
        onChange={(e) => {
          onChange &&
            onChange({ query: e.target.value, showAll: showAll || false })
        }}
      />
      <Checkbox
        label="Show all"
        title="Include completed checkouts"
        className="CheckoutSearch-showAll"
        checked={showAll}
        onChange={(e) => {
          onChange &&
            onChange({ query: value || "", showAll: e.target.checked })
        }}
      />
    </Group>
  )
}

export type SearchResultsProps = {
  results?: CheckoutListResponse[]
  onSelect?: (row: CheckoutListResponse) => void
  getLink?: (row: CheckoutListResponse) => string | null | undefined
}

const Results = (props: SearchResultsProps) => {
  const { results, onSelect, getLink } = props

  if (!!results && results.length == 0) {
    return <Search.NoResults />
  }

  if (!results) {
    return
  }

  return (
    <Table.ScrollContainer
      className="CheckoutSearch-scrollContainer"
      minWidth={500}
    >
      <Table className="CheckoutSearch-table">
        <Table.Thead>
          <Table.Tr>
            <Table.Th></Table.Th>
            <Table.Th>Service</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Email</Table.Th>
            <Table.Th>ID</Table.Th>
            <Table.Th>Status</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {results?.map((checkout) => {
            const link = getLink ? getLink(checkout) : undefined
            return (
              <Table.Tr
                key={checkout.id}
                onClick={() => {
                  if (onSelect) {
                    onSelect(checkout)
                  }
                }}
              >
                <Table.Td>
                  <ActionIcon
                    className="CheckoutSearch-cartButton"
                    variant="subtle"
                    c="gray"
                    size="sm"
                    component="a"
                    href={link ?? undefined}
                    onClick={(e) => {
                      e.preventDefault()
                    }}
                  >
                    <IconShoppingCartShare />
                  </ActionIcon>
                </Table.Td>
                <Table.Td>{checkout.service}</Table.Td>
                <Table.Td>{formatName(checkout)}</Table.Td>
                <Table.Td>{checkout.email}</Table.Td>
                <Table.Td>{checkout.id}</Table.Td>
                <Table.Td>{formatState(checkout.state)}</Table.Td>
              </Table.Tr>
            )
          })}
        </Table.Tbody>
      </Table>
    </Table.ScrollContainer>
  )
}

export const NoResults = () => {
  return (
    <Text className="CheckoutSearch-noResults" c="gray">
      No results
    </Text>
  )
}

Search.NoResults = NoResults
Search.Input = Input
Search.Results = Results

const formatName = (checkout: CheckoutListResponse) => {
  return [checkout.first_name, checkout.last_name].filter((v) => !!v).join(" ")
}

const formatState = (state: CheckoutState): string => {
  switch (state) {
    case CheckoutState.canceled:
      return "Canceled"
    case CheckoutState.complete:
      return "Complete"
    case CheckoutState.pending:
      return "Pending"
    default:
      return state
  }
}
