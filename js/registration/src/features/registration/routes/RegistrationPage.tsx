import { Subtitle, Title } from "#src/components"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useCheckoutAPI } from "#src/features/checkout/hooks"
import { CheckoutState } from "#src/features/checkout/types/Checkout"
import { useEventAPI } from "#src/features/event/hooks"
import {
  InterviewDialog,
  useInterviewRecordStore,
} from "#src/features/interview"
import {
  Registration as IRegistration,
  RegistrationState,
} from "#src/features/registration"
import { Registration } from "#src/features/registration/components/registration/registration/Registration"
import { useRegistrationAPI } from "#src/features/registration/hooks"
import { useWretch } from "#src/hooks/api"
import { useConfirm } from "#src/hooks/confirm"
import { useLocation, useNavigate } from "#src/hooks/location"
import {
  Anchor,
  Button,
  Group,
  Select,
  Skeleton,
  Stack,
  Table,
} from "@mantine/core"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"
import { IconCheck, IconEdit, IconTrash } from "@tabler/icons-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import dayjs from "dayjs"
import { observer } from "mobx-react-lite"
import { useState } from "react"
import { Link, useParams } from "react-router-dom"

export const RegistrationPage = observer(() => {
  const { registrationId = "" } = useParams()

  const eventAPI = useEventAPI()
  const registrationAPI = useRegistrationAPI()
  const checkoutAPI = useCheckoutAPI()

  const confirm = useConfirm()
  const loc = useLocation()
  const navigate = useNavigate()
  const interviewStore = useInterviewRecordStore()

  const authStore = useAuth()
  const wretch = useWretch()
  const editable = !!authStore.authInfo?.hasScope(Scope.registrationEdit)
  const viewCheckouts = !!authStore.authInfo?.hasScope(Scope.checkout)

  const client = useQueryClient()
  const events = useQuery(eventAPI.list())
  const regQuery = registrationAPI.read(registrationId)
  const registration = useQuery(regQuery)
  const checkouts = useQuery({
    ...checkoutAPI.list(undefined, {
      registrationId: registrationId,
      showAll: true,
    }),
    enabled: viewCheckouts,
  })

  const changeInterviews = useQuery(
    registrationAPI.listChangeInterviews(registrationId),
  )

  const update = useMutation({
    ...registrationAPI.update(),
    onSuccess(data) {
      client.setQueryData(regQuery.queryKey, data)
    },
  })

  const complete = useMutation({
    ...registrationAPI.complete(registrationId),
    onSuccess(data) {
      client.setQueryData(regQuery.queryKey, data)
    },
  })

  const cancel = useMutation({
    ...registrationAPI.cancel(registrationId),
    onSuccess(data) {
      client.setQueryData(regQuery.queryKey, data)
    },
  })

  const [edit, setEdit] = useState(false)

  if (!registration.isSuccess) {
    return <Placeholder />
  }

  const reg = registration.data

  return (
    <Title title={formatName(reg)}>
      <Subtitle subtitle="View registration">
        <Anchor component={Link} to="/registrations">
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
                  complete.mutate()
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
                  confirm("Confirm", "Cancel registration?").then((res) => {
                    if (res) {
                      cancel.mutate()
                    }
                  })
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
          events={events.data}
          editable={edit}
          onCancel={() => setEdit(false)}
          onSave={async (reg) => {
            await update.mutateAsync(reg)
            setEdit(false)
          }}
        />
        {viewCheckouts && (
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Service</Table.Th>
                <Table.Th>Receipt</Table.Th>
                <Table.Th>ID</Table.Th>
                <Table.Th>State</Table.Th>
                <Table.Th>Date</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {checkouts.data.map((c) => (
                <Table.Tr key={c.id}>
                  <Table.Td>{c.service}</Table.Td>
                  <Table.Td>
                    {c.receipt_url ? (
                      <Anchor href={c.receipt_url} target={c.receipt_id}>
                        {c.receipt_id}
                      </Anchor>
                    ) : (
                      c.receipt_id
                    )}
                  </Table.Td>
                  <Table.Td>
                    {c.url ? <Anchor href={c.url}>{c.id}</Anchor> : c.id}
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
        {changeInterviews.isSuccess && changeInterviews.data.length > 0 && (
          <Group>
            <Select
              placeholder="Choose Action"
              data={changeInterviews.data.map((opt) => ({
                label: opt.name,
                value: opt.id,
              }))}
              value={null}
              onChange={async (id) => {
                if (!id) {
                  return
                }

                const state = await client.ensureQueryData(
                  registrationAPI.readChangeInterview(registrationId, id),
                )
                const record = await startInterview(
                  interviewStore,
                  defaultAPI,
                  state,
                  {
                    registrationId: registrationId,
                  },
                )
                navigate(loc, {
                  state: {
                    ...loc.state,
                    showInterviewDialog: {
                      recordId: record.id,
                    },
                  },
                })
              }}
            />
          </Group>
        )}
        <InterviewDialog.Manager
          onComplete={async (r) => {
            const response = r.stateResponse
            if (
              response.complete &&
              response.target_url &&
              r.metadata.registrationId
            ) {
              const res = await wretch
                .url(response.target_url, true)
                .json({ state: response.state })
                .put()
                .json()

              client.invalidateQueries({
                queryKey: registrationAPI.listChangeInterviews(
                  r.metadata.registrationId,
                ).queryKey,
              })
              client.setQueryData(
                registrationAPI.read(registrationId).queryKey,
                res,
              )
              navigate(loc, {
                state: { ...loc.state, showInterviewDialog: undefined },
              })
            }
          }}
        />
      </Subtitle>
    </Title>
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
