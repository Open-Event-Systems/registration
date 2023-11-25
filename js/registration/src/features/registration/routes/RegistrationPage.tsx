import { Subtitle, Title } from "#src/components"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useEvents } from "#src/features/event/hooks"
import { Await } from "#src/features/loader"
import {
  Registration as IRegistration,
  RegistrationState,
} from "#src/features/registration"
import { Registration } from "#src/features/registration/components/registration/registration/Registration"
import { useRegistrationStore } from "#src/features/registration/hooks"
import { Anchor, Button, Group, Skeleton, Stack } from "@mantine/core"
import { IconCheck, IconEdit, IconTrash } from "@tabler/icons-react"
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
