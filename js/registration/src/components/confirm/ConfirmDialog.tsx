import { ModalDialog, ModalDialogProps } from "#src/components"
import { ConfirmContext } from "#src/hooks/confirm"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Button, Group, Stack, Text } from "@mantine/core"
import { IconCheck, IconX } from "@tabler/icons-react"
import { observer } from "mobx-react-lite"
import { useContext, useEffect } from "react"

export const ConfirmationDialog = observer(() => {
  const ctx = useContext(ConfirmContext)
  const curConfirmation = ctx.get()
  const loc = useLocation()
  const navigate = useNavigate()

  const show = !!loc.state?.showConfirm && !!curConfirmation

  useEffect(() => {
    if (!show) {
      curConfirmation && curConfirmation.cancel()
    }
  }, [show])

  return (
    <ModalDialog
      title={curConfirmation?.title}
      opened={show}
      onClose={() => {
        navigate(-1)
      }}
    >
      <Stack>
        <Text>{curConfirmation?.message}</Text>
        <Group>
          <Button
            leftSection={<IconCheck />}
            variant="primary"
            onClick={() => {
              curConfirmation && curConfirmation.confirm()
              navigate(-1)
            }}
          >
            Confirm
          </Button>
          <Button
            leftSection={<IconX />}
            variant="outline"
            color="red"
            onClick={() => {
              curConfirmation && curConfirmation.cancel()
              navigate(-1)
            }}
          >
            Cancel
          </Button>
        </Group>
      </Stack>
    </ModalDialog>
  )
})
