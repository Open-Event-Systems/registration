import { Subtitle, Title } from "#src/components"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useEvents } from "#src/features/event/hooks"
import { Await } from "#src/features/loader"
import { Registration as IRegistration } from "#src/features/registration"
import { Registration } from "#src/features/registration/components/registration/registration/Registration"
import { useRegistrationStore } from "#src/features/registration/hooks"
import { Button, Group, Skeleton, Stack } from "@mantine/core"
import { IconEdit } from "@tabler/icons-react"
import { observer } from "mobx-react-lite"
import { useState } from "react"
import { useParams } from "react-router-dom"

export const RegistrationPage = observer(() => {
  const events = useEvents()
  const regStore = useRegistrationStore()
  const { registrationId = "" } = useParams()

  const authStore = useAuth()
  const editable =
    !!authStore.authInfo?.hasScope(Scope.registrationEdit) || true

  const reg = regStore.getOrFetch(registrationId)

  const [edit, setEdit] = useState(false)
  const onSave = async (reg: IRegistration) => {
    await regStore.update(reg)
  }

  return (
    <Await value={reg} fallback={<Placeholder />}>
      {(reg) => {
        return (
          <Title title={formatName(reg)}>
            <Subtitle subtitle="View registration">
              <Registration
                key={`${reg.id}-${reg.version}`}
                registration={reg}
                events={new Map(Array.from(events, (e) => [e.id, e]))}
                editable={edit}
                onCancel={() => setEdit(false)}
                onSave={(reg) => {
                  onSave(reg).then(() => setEdit(false))
                }}
              />
              <Group>
                {editable && !edit && (
                  <Button
                    leftSection={<IconEdit />}
                    variant="subtle"
                    onClick={() => setEdit(true)}
                  >
                    Edit
                  </Button>
                )}
              </Group>
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
