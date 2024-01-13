import { UserMenu } from "#src/components"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { SettingsDialog } from "#src/features/checkin/components/settings-dialog/SettingsDialog"
import { StationSelect } from "#src/features/checkin/components/station-select/StationSelect"
import { useCheckInStore } from "#src/features/checkin/hooks"
import {
  CheckInStore,
  CheckInStoreContext,
} from "#src/features/checkin/stores/CheckInStore"
import { useQueueAPI } from "#src/features/queue/hooks"
import { StationSettings } from "#src/features/queue/types"
import { useApp } from "#src/hooks/app"
import { NotFoundError } from "#src/utils/api"
import { ActionIcon, Box, BoxProps, Switch } from "@mantine/core"
import { IconSettings } from "@tabler/icons-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
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
  const queueAPI = useQueueAPI()
  const [checkInStore] = useState(() => new CheckInStore(app.wretch))

  if (auth.ready && !!auth.authInfo && !auth.authInfo.hasScope(Scope.checkIn)) {
    throw new NotFoundError()
  }

  // list stations
  useQuery({
    ...queueAPI.listStations(),
    refetchOnMount: false,
  })

  const stationInfo = useQuery({
    ...queueAPI.getStation(checkInStore.stationId ?? ""),
    refetchOnMount: false,
    enabled: !!checkInStore.stationId,
  })

  // refetch queue items
  useQuery({
    ...queueAPI.listQueueItems(
      stationInfo.data?.group_id ?? "",
      stationInfo.data?.id,
    ),
    enabled: stationInfo.isSuccess,
    staleTime: 5000,
    refetchInterval: 5000,
  })

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
    const stations = useQuery({
      ...queueAPI.listStations(),
      staleTime: Infinity,
    })
    const stationInfo = useQuery({
      ...queueAPI.getStation(checkInStore.stationId ?? ""),
      staleTime: Infinity,
      enabled: !!checkInStore.stationId,
    })

    const setStationSettings = useMutation(
      queueAPI.setStationSettings(checkInStore.stationId ?? ""),
    )

    const [showSettingsDialog, setShowSettingsDialog] = useState(false)

    return (
      <Box className="CheckinLayout-header" {...other}>
        {children}
        <CheckinLayout.Spacer />
        <Switch
          label="Open"
          labelPosition="left"
          checked={!!stationInfo.data?.settings.open}
          disabled={!stationInfo.data || !checkInStore.stationId}
          onChange={(e) => {
            if (stationInfo.data) {
              setStationSettings.mutate({
                ...stationInfo.data.settings,
                open: e.target.checked,
              })
            }
          }}
        />
        <StationSelect
          value={checkInStore.stationId}
          options={stations.data?.map((s) => s.id) ?? []}
          onChange={action((opt) => {
            checkInStore.stationId = opt
          })}
        />
        <ActionIcon
          variant="subtle"
          c="gray"
          onClick={() => {
            if (stationInfo.isSuccess) {
              setShowSettingsDialog(true)
            }
          }}
        >
          <IconSettings />
        </ActionIcon>
        <UserMenu
          username={auth.authInfo?.email || "Guest"}
          onSignOut={() => {
            auth.signOut()
          }}
        />
        <SettingsDialog
          opened={showSettingsDialog}
          onClose={() => setShowSettingsDialog(false)}
          stationIds={stations.data?.map((s) => s.id) ?? []}
          settings={stationInfo.data?.settings ?? ({} as StationSettings)}
          onChange={(settings) => {
            setStationSettings.mutate(settings)
            setShowSettingsDialog(false)
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
