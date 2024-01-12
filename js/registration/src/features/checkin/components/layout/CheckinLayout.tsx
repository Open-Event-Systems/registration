import { UserMenu } from "#src/components"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { StationSelect } from "#src/features/checkin/components/station-select/StationSelect"
import { useCheckInStore } from "#src/features/checkin/hooks"
import {
  CheckInStore,
  CheckInStoreContext,
} from "#src/features/checkin/stores/CheckInStore"
import { useQueueAPI } from "#src/features/queue/hooks"
import { useApp } from "#src/hooks/app"
import { NotFoundError } from "#src/utils/api"
import { Box, BoxProps } from "@mantine/core"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import clsx from "clsx"
import { action } from "mobx"
import { observer } from "mobx-react-lite"
import {
  ComponentPropsWithRef,
  ComponentPropsWithoutRef,
  ReactNode,
  useState,
} from "react"

const _CheckinLayout = observer(({ children }: { children?: ReactNode }) => {
  const app = useApp()
  const auth = useAuth()
  const queryClient = useQueryClient()
  const queueAPI = useQueueAPI()
  const [checkInStore] = useState(() => new CheckInStore(queryClient, queueAPI))

  if (auth.ready && !!auth.authInfo && !auth.authInfo.hasScope(Scope.checkIn)) {
    throw new NotFoundError()
  }

  return (
    <Box className="CheckinLayout-root">
      <CheckInStoreContext.Provider value={checkInStore}>
        {children}
      </CheckInStoreContext.Provider>
      <SignInDialog.Manager authStore={app.authStore} wretch={app.wretch} />
    </Box>
  )
})

_CheckinLayout.displayName = "CheckinLayout"

export const CheckinLayout = (props: { children?: ReactNode }) => (
  <_CheckinLayout {...props} />
)

const CheckinLayoutHeader = observer(
  (props: BoxProps & ComponentPropsWithRef<"div">) => {
    const { children, ...other } = props

    const auth = useAuth()
    const checkInStore = useCheckInStore()

    const queueAPI = useQueueAPI()
    const stations = useQuery(queueAPI.listStations())

    return (
      <Box className="CheckinLayout-header" {...other}>
        {children}
        <CheckinLayout.Spacer />
        <StationSelect
          options={stations.data?.map((s) => s.id) ?? []}
          onChange={action((opt) => {
            checkInStore.stationId = opt
          })}
        />
        <UserMenu
          username={auth.authInfo?.email || "Guest"}
          onSignOut={() => {
            auth.signOut()
          }}
        />
      </Box>
    )
  },
)

CheckinLayoutHeader.displayName = "CheckinLayoutHeader"

CheckinLayout.Header = CheckinLayoutHeader

const CheckinLayoutSpacer = (
  props: BoxProps & ComponentPropsWithRef<"div">,
) => {
  return <Box className="CheckinLayout-spacer" {...props} />
}

CheckinLayout.Spacer = CheckinLayoutSpacer

const CheckinLayoutLeft = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-left", className)} {...other} />
}

CheckinLayout.Left = CheckinLayoutLeft

const CheckinLayoutCenter = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-center", className)} {...other} />
}

CheckinLayout.Center = CheckinLayoutCenter

const CheckinLayoutRight = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-right", className)} {...other} />
}

CheckinLayout.Right = CheckinLayoutRight

const CheckinLayoutBody = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-body", className)} {...other} />
}

CheckinLayout.Body = CheckinLayoutBody
