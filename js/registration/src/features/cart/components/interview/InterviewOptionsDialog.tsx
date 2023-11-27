import { ButtonList } from "#src/components/button-list/ButtonList"
import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog"
import { useCartAPI } from "#src/features/cart/hooks"
import { InterviewOption } from "#src/features/cart/types"
import { useInterviewRecordStore } from "#src/features/interview"
import { useLocation, useNavigate } from "#src/hooks/location"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"
import { useQueryClient } from "@tanstack/react-query"
import { useEffect, useLayoutEffect, useState } from "react"

declare module "#src/hooks/location" {
  interface LocationState {
    showInterviewOptionsDialog?: { eventId: string; cartId: string }
  }
}

export type InterviewOptionsDialogProps = {
  options: InterviewOption[]
  onSelect?: (option: InterviewOption) => void | Promise<void>
} & Omit<ModalDialogProps, "children" | "onSelect">

export const InterviewOptionsDialog = (props: InterviewOptionsDialogProps) => {
  const { options, onSelect, ...other } = props

  const [loading, setLoading] = useState(false)

  return (
    <ModalDialog title="Select An Option" loading={loading} {...other}>
      <ButtonList>
        {options.map((opt, i) => (
          <ButtonList.Button
            key={i}
            onClick={() => {
              if (onSelect) {
                if (loading) {
                  return
                }

                const res = onSelect(opt)
                if (res && "then" in res) {
                  setLoading(true)
                  res.finally(() => {
                    setLoading(false)
                  })
                }
              }
            }}
          >
            {opt.name || opt.id}
          </ButtonList.Button>
        ))}
      </ButtonList>
    </ModalDialog>
  )
}

const Manager = (props: InterviewOptionsDialogProps) => {
  const { options } = props

  const loc = useLocation()
  const navigate = useNavigate()
  const cartAPI = useCartAPI()
  const recordStore = useInterviewRecordStore()

  const showData = loc.state?.showInterviewOptionsDialog
  const show = !!showData
  const eventId = showData?.eventId ?? ""
  const cartId = showData?.cartId ?? ""

  const client = useQueryClient()

  const [prevOptions, setPrevOptions] = useState(options)

  useLayoutEffect(() => {
    if (show) {
      setPrevOptions(options)
    }
  }, [show, options])

  const handleSelect = async (opt: InterviewOption) => {
    const response = await client.fetchQuery(
      cartAPI.readAddInterview(cartId, opt.id),
    )
    const record = await startInterview(recordStore, defaultAPI, response, {
      cartId: cartId,
      eventId: eventId,
    })
    navigate(loc, {
      state: {
        showInterviewDialog: {
          eventId: eventId,
          recordId: record.id,
        },
      },
      replace: true,
    })
  }

  useEffect(() => {
    if (show && options.length == 1) {
      handleSelect(options[0])
    }
  }, [show, options])

  return (
    <InterviewOptionsDialog
      {...props}
      opened={show && options.length != 1}
      options={show ? options : prevOptions}
      onSelect={handleSelect}
      onClose={() => {
        navigate(-1)
      }}
    />
  )
}

InterviewOptionsDialog.Manager = Manager
