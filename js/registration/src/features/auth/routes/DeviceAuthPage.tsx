import {
  DeviceAuthorization,
  DeviceAuthorizationOptions,
} from "#src/features/auth/components/device/auth/DeviceAuthorization"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useWretch } from "#src/hooks/api"
import { useLocation, useNavigate } from "#src/hooks/location"
import {
  Box,
  Button,
  LoadingOverlay,
  Skeleton,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core"
import { useIsMutating, useMutation, useQuery } from "@tanstack/react-query"
import { useLayoutEffect, useState } from "react"
import { WretchResponse } from "wretch"

export const DeviceAuthPage = () => {
  const auth = useAuth()
  const wretch = useWretch()
  const loc = useLocation()
  const navigate = useNavigate()

  const code = loc.hash.startsWith("#user_code=")
    ? loc.hash.substring(11)
    : undefined

  const showOptions = !!auth.authInfo?.hasScope(Scope.admin)

  const codeQuery = useQuery({
    // TODO: move this elsewhere
    queryKey: ["auth", "device", code],
    async queryFn() {
      return await wretch
        .url("/auth/check-authorize-device")
        .json({ user_code: code?.toUpperCase() })
        .post()
        .forbidden(() => null)
        .json<{ client: string; scope: string }>()
    },
    staleTime: Infinity,
    enabled: !!code,
  })

  const authorizeMutation = useMutation({
    mutationKey: ["auth", "complete-authorize-device", code],
    async mutationFn(options: DeviceAuthorizationOptions) {
      const body: Record<string, unknown> = {
        user_code: code?.toUpperCase(),
      }

      if (showOptions) {
        body.scope = options.scope.join(" ")

        if (options.account != "my_account") {
          body.new_account = true
        }

        if (options.account == "new_account" && options.email) {
          body.email = options.email
        }

        if (options.requireWebAuthn) {
          body.require_webauthn = true
        }
      }

      const res = await wretch
        .url("/auth/complete-authorize-device")
        .json(body)
        .post()
        .forbidden(() => false)
        .res<WretchResponse | false>()

      if (res == false) {
        throw new Error("Authorization failed")
      }
    },
  })

  useLayoutEffect(() => {
    authorizeMutation.reset()
  }, [code])

  const isMutating = useIsMutating({
    mutationKey: ["auth", "complete-authorize-device", code],
  })

  let content

  if (!code) {
    content = <CodeInput />
  } else if (codeQuery.isPending) {
    content = <Placeholder />
  } else if (codeQuery.isError || codeQuery.data === null) {
    content = <InvalidCode />
  } else if (authorizeMutation.isError) {
    content = <AuthFailed />
  } else if (authorizeMutation.isSuccess) {
    content = <Success />
  } else {
    content = (
      <DeviceAuthorization
        client={codeQuery.data.client}
        scope={codeQuery.data.scope.split(" ")}
        showOptions={showOptions}
        onCancel={() => navigate(-1)}
        onComplete={(options) => {
          authorizeMutation.mutate(options)
        }}
      />
    )
  }

  return (
    <Box
      p={16}
      style={{
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "stretch",
        maxWidth: 500,
      }}
    >
      {content}
      <LoadingOverlay visible={isMutating > 0} />
    </Box>
  )
}

const Placeholder = () => (
  <Stack>
    <Skeleton h="2.25rem" />
    <Skeleton h="1.25rem" />
    <Skeleton h="1.25rem" />
    <Skeleton h="1.25rem" />
  </Stack>
)

const CodeInput = () => {
  const [code, setCode] = useState("")
  const loc = useLocation()
  const navigate = useNavigate()

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (code) {
          navigate({ ...loc, hash: `#user_code=${code}` })
        }
      }}
      style={{
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "stretch",
      }}
    >
      <Stack style={{ flex: "auto" }}>
        <Title order={3}>Enter Code</Title>
        <TextInput value={code} onChange={(e) => setCode(e.target.value)} />
        <div style={{ flex: "auto" }} />
        <Button variant="filled" type="submit">
          Verify
        </Button>
      </Stack>
    </form>
  )
}

const Success = () => (
  <Stack>
    <Title order={3}>Authorization Successful</Title>
    <Text component="p">Authorization was successful.</Text>
  </Stack>
)

const InvalidCode = () => (
  <Stack>
    <Title order={3}>Invalid Code</Title>
    <Text component="p">The code was not valid.</Text>
  </Stack>
)

const AuthFailed = () => (
  <Stack>
    <Title order={3}>Authorization Failed</Title>
    <Text component="p">
      Authorization failed. The code may have expired or already been used.
    </Text>
  </Stack>
)
