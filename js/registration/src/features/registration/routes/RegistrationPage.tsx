import { Subtitle, Title } from "#src/components"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { CheckoutState } from "#src/features/checkout/types/Checkout"
import { useEvents } from "#src/features/event/hooks"
import { Await, useLoader } from "#src/features/loader"
import {
  Registration as IRegistration,
  RegistrationState,
} from "#src/features/registration"
import { Registration } from "#src/features/registration/components/registration/registration/Registration"
import { useRegistrationStore } from "#src/features/registration/hooks"
import { Anchor, Button, Group, Skeleton, Stack, Table } from "@mantine/core"
import { IconCheck, IconEdit, IconTrash } from "@tabler/icons-react"
import dayjs from "dayjs"
import { observer } from "mobx-react-lite"
import { useState } from "react"
import { Link, useParams } from "react-router-dom"

export const RegistrationPage = observer(() => {
  const events = useEvents()
  const regStore = useRegistrationStore()
  const { registrationId = "" } = useParams()

  const authStore = useAuth()
  const editable =
    !!authStore.authInfo?.hasScope(Scope.registrationEdit) || true

  const reg = regStore.getOrFetch(registrationId)

  const [edit, setEdit] = useState(false)
  const checkouts = useLoader(
    () => regStore.readCheckouts(registrationId),
    [registrationId],
  )

  return (
    <Await value={reg} fallback={<Placeholder />}>
      {(reg) => {
        return (
          <Title title={formatName(reg)}>
            <Subtitle subtitle="View registration">
              <Anchor component={Link} to="/">
                &laquo; Back to registrations
              </Anchor>
              {editable && !edit && (
                <Group>
                  <Button
                    leftSection={<IconEdit />}
                    variant="outline"
                    onClick={() => setEdit(true)}
                  >
                    Edit
                  </Button>
                  {reg.state == RegistrationState.pending && (
                    <Button
                      leftSection={<IconCheck />}
                      variant="outline"
                      onClick={() => {
                        regStore.complete(reg.id)
                      }}
                    >
                      Complete Registration
                    </Button>
                  )}
                  {reg.state != RegistrationState.canceled && (
                    <Button
                      leftSection={<IconTrash />}
                      variant="outline"
                      color="red"
                      onClick={() => {
                        regStore.cancel(reg.id)
                      }}
                    >
                      Cancel Registration
                    </Button>
                  )}
                </Group>
              )}
              <Registration
                key={`${reg.id}-${reg.version}`}
                registration={reg}
                events={new Map(Array.from(events, (e) => [e.id, e]))}
                editable={edit}
                onCancel={() => setEdit(false)}
                onSave={async (reg) => {
                  await regStore.update(reg)
                  setEdit(false)
                }}
              />
              <Await value={checkouts}>
                {(checkouts) => (
                  <Table>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Service</Table.Th>
                        <Table.Th>ID</Table.Th>
                        <Table.Th>State</Table.Th>
                        <Table.Th>Date</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {checkouts.map((c) => (
                        <Table.Tr key={c.id}>
                          <Table.Td>{c.service}</Table.Td>
                          <Table.Td>
                            {c.url ? (
                              <Anchor href={c.url}>{c.id}</Anchor>
                            ) : (
                              c.id
                            )}
                          </Table.Td>
                          <Table.Td>{formatState(c.state)}</Table.Td>
                          <Table.Td>
                            {dayjs(c.date).format("YYYY-MM-DD HH:mm Z")}
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                )}
              </Await>
            </Subtitle>
          </Title>
        )
      }}
    </Await>
  )
})

RegistrationPage.displayName = "RegistrationPage"

const Placeholder = () => (
  <Stack gap="md">
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
    <Group>
      <Skeleton h="1.5rem" w={120} />
      <Skeleton h="1.5rem" w={300} />
    </Group>
  </Stack>
)

const formatName = (r: IRegistration) => {
  const names = [r.preferred_name || r.first_name, r.last_name]
    .filter((v) => !!v)
    .join(" ")
  return names || r.email || "Registration"
}

const formatState = (c: CheckoutState) => {
  switch (c) {
    case CheckoutState.pending:
      return "Pending"
    case CheckoutState.canceled:
      return "Canceled"
    case CheckoutState.complete:
      return "Complete"
  }
}
