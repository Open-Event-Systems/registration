import { ButtonList } from "#src/components/button_list/ButtonList.js"
import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { useCartStore, useCurrentCartStore } from "#src/features/cart/hooks.js"
import { AccessCodeOptions } from "#src/features/selfservice/components/access-code/AccessCodeOptions.js"
import { SelfServiceRegistrationListResponse } from "#src/features/selfservice/types.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import { Text } from "@mantine/core"
import { action } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ReactNode } from "react"

export type AccessCodeOptionsDialogProps = {
  response: SelfServiceRegistrationListResponse
  registrationId?: string
  onSelect?: (interviewId?: string, registrationId?: string) => void
} & Omit<ModalDialogProps, "onSelect" | "children">

export const AccessCodeOptionsDialog = (
  props: AccessCodeOptionsDialogProps
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
          registrations={response.registrations.map((r) => r.registration)}
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
      (r) => r.registration.id == registrationId
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
                onSelect && onSelect(registrationId, opt.id)
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
  (props: AccessCodeOptionsDialogProps & { accessCode?: string }) => {
    const loc = useLocation()
    const navigate = useNavigate()
    const cartStore = useCartStore()
    const currentCartStore = useCurrentCartStore()

    const { accessCode, ...other } = props

    const state = useLocalObservable(() => ({
      loading: false,
    }))

    return (
      <AccessCodeOptionsDialog
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
              const record = await cartStore.startInterview(
                currentCartStore,
                interviewId,
                registrationId,
                accessCode
              )

              navigate(loc, {
                state: {
                  ...loc.state,
                  accessCodeDialogRegistrationId: undefined,
                  showInterviewDialog: {
                    eventId: currentCartStore.eventId,
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
  }
)

AccessCodeOptionsDialog.Manager = AccessCodeOptionsDialogManager
