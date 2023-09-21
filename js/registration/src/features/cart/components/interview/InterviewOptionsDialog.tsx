import { ButtonList } from "#src/components/button_list/ButtonList.js"
import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { useCartStore, useCurrentCartStore } from "#src/features/cart/hooks.js"
import { InterviewOption } from "#src/features/cart/types.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import { useEffect, useLayoutEffect, useState } from "react"

declare module "#src/hooks/location.js" {
  interface LocationState {
    showInterviewOptionsDialog?: string
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
  const cartStore = useCartStore()
  const currentCartStore = useCurrentCartStore()

  const [prevOptions, setPrevOptions] = useState(options)

  const show = currentCartStore.eventId == loc.state?.showInterviewOptionsDialog

  useLayoutEffect(() => {
    if (show) {
      setPrevOptions(options)
    }
  }, [show, options])

  const handleSelect = async (opt: InterviewOption) => {
    const record = await cartStore.startInterview(currentCartStore, opt.id)
    navigate(loc, {
      state: {
        showInterviewDialog: {
          eventId: currentCartStore.eventId,
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
