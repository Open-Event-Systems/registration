import { ButtonList } from "#src/components/button-list/ButtonList"
import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog"
import { useCartAPI } from "#src/features/cart/hooks"
import { useInterviewRecordStore } from "#src/features/interview"
import { AccessCodeOptions } from "#src/features/selfservice/components/access-code/AccessCodeOptions"
import { SelfServiceRegistrationListResponse } from "#src/features/selfservice/types"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Text } from "@mantine/core"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"
import { useQueryClient } from "@tanstack/react-query"
import { action } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ReactNode } from "react"

export type AccessCodeOptionsDialogProps = {
  response: SelfServiceRegistrationListResponse
  registrationId?: string
  onSelect?: (interviewId?: string, registrationId?: string) => void
} & Omit<ModalDialogProps, "onSelect" | "children">

export const AccessCodeOptionsDialog = (
  props: AccessCodeOptionsDialogProps,
) => {
  const { response, registrationId, onSelect, ...other } = props

  let title: ReactNode
  let content

  if (!registrationId) {
    title = "Access Code"
    content = (
      <>
        <Text component="p">
          You are using an access code. Choose a registration to change, or
          create a new registration.
        </Text>
        <AccessCodeOptions
          registrations={response.registrations
            .filter((r) => r.change_options.length > 0)
            .map((r) => r.registration)}
          interviews={response.add_options}
          onSelectAdd={(id) => {
            onSelect && onSelect(id)
          }}
          onSelectChange={(id) => {
            onSelect && onSelect(undefined, id)
          }}
        />
      </>
    )
  } else {
    title = "Change Registration"

    const registration = response.registrations.find(
      (r) => r.registration.id == registrationId,
    )
    const options = registration?.change_options ?? []

    content = (
      <>
        <Text component="p">Select an option to change this registration.</Text>
        <ButtonList>
          {options.map((opt, i) => (
            <ButtonList.Button
              key={i}
              onClick={() => {
                onSelect && onSelect(opt.id, registrationId)
              }}
            >
              {opt.name || opt.id}
            </ButtonList.Button>
          ))}
        </ButtonList>
      </>
    )
  }

  return (
    <ModalDialog title={title} hideCloseButton {...other}>
      {content}
    </ModalDialog>
  )
}

const AccessCodeOptionsDialogManager = observer(
  (
    props: AccessCodeOptionsDialogProps & {
      accessCode?: string
      eventId: string
      cartId: string
    },
  ) => {
    const { accessCode, eventId, cartId, ...other } = props
    const loc = useLocation()
    const navigate = useNavigate()

    const client = useQueryClient()
    const cartAPI = useCartAPI()
    const recordStore = useInterviewRecordStore()

    const state = useLocalObservable(() => ({
      loading: false,
    }))

    return (
      <AccessCodeOptionsDialog
        registrationId={loc.state?.accessCodeDialogRegistrationId}
        onSelect={action(async (interviewId, registrationId) => {
          if (state.loading) {
            return
          }

          state.loading = true
          try {
            if (!interviewId && registrationId) {
              navigate(loc, {
                state: {
                  ...loc.state,
                  accessCodeDialogRegistrationId: registrationId,
                },
              })
            } else if (interviewId) {
              const response = await client.fetchQuery(
                cartAPI.readAddInterview(cartId, interviewId, {
                  accessCode: accessCode,
                  registrationId: registrationId,
                }),
              )
              const record = await startInterview(
                recordStore,
                defaultAPI,
                response,
                { eventId: eventId, cartId: cartId },
              )

              navigate(loc, {
                state: {
                  ...loc.state,
                  accessCodeDialogRegistrationId: undefined,
                  showInterviewDialog: {
                    eventId: eventId,
                    recordId: record.id,
                  },
                },
              })
            }
          } finally {
            state.loading = false
          }
        })}
        {...other}
      />
    )
  },
)

AccessCodeOptionsDialog.Manager = AccessCodeOptionsDialogManager
