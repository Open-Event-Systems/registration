import { placeholderWretch } from "#src/config/api"
import { AuthAPIContext } from "#src/features/auth/api"
import { signInComponents, signInOptions } from "#src/features/auth/options"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo"
import { AuthStore, JS_CLIENT_ID } from "#src/features/auth/stores/AuthStore"
import { AuthAPI } from "#src/features/auth/types/api"
import { setSavedWebAuthnCredentialId } from "#src/features/auth/webauthn"
import { useLocation, useNavigate } from "#src/hooks/location"
import {
  browserSupportsWebAuthn,
  platformAuthenticatorIsAvailable,
} from "@simplewebauthn/browser"
import { useIsMutating, useMutation, useQuery } from "@tanstack/react-query"
import { TokenEndpointResponse } from "oauth4webapi"
import {
  ComponentType,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react"

const defaultAuthStore = new AuthStore(
  new URL(window.location.href),
  placeholderWretch,
)

export const AuthContext = createContext(defaultAuthStore)

export const useAuth = () => useContext(AuthContext)

export const useAuthAPI = () => useContext(AuthAPIContext)

export enum SignInStep {
  signIn = "signIn",
  webAuthn = "webAuthn",
}

export type SignInState = {
  readonly step: SignInStep
  readonly api: AuthAPI
  readonly tokenResponse: TokenEndpointResponse | null
  readonly updating: boolean
  readonly signInOptions: [string, ComponentType][] | null
  readonly signInComponent: ComponentType | null
  getAccount(): Promise<TokenEndpointResponse>
  selectOptionId(optionId: string): void
  completeSignIn(tokenResponse: TokenEndpointResponse): void
  completeRegistration(tokenResponse: TokenEndpointResponse): void
  completeWebAuthnRegistration(credentialId: string | null): void
}

export const SignInStateContext = createContext<SignInState | null>(null)

export const useSignInState = () => {
  const state = useContext(SignInStateContext)
  if (!state) {
    throw new Error("No sign in state configured")
  }
  return state
}

export const createSignIn = (clientId = JS_CLIENT_ID): SignInState => {
  const loc = useLocation()
  const navigate = useNavigate()
  const auth = useAuth()
  const api = useAuthAPI()

  const optionId = loc.state?.signInOption

  const [step, setStep] = useState(SignInStep.signIn)
  const [curToken, setCurToken] = useState<TokenEndpointResponse | null>(null)

  const webAuthnAvailable = useQuery({
    queryKey: ["webauthn-availability"],
    async queryFn() {
      return await getWebAuthnAvailability()
    },
    staleTime: Infinity,
  })

  const signInOptionsQuery = useQuery({
    queryKey: ["auth", "options"],
    async queryFn() {
      const available = await Promise.all(
        Object.entries(signInOptions).map(([id, opt]) =>
          opt().then((res): [string, ComponentType | null] => [id, res]),
        ),
      )
      return available.filter((v): v is [string, ComponentType] => !!v[1])
    },
    staleTime: Infinity,
  })

  const signInComponentQuery = useQuery({
    queryKey: ["auth", "component", optionId],
    async queryFn() {
      if (!optionId) {
        return null
      }

      const factory = signInComponents[optionId]
      if (factory) {
        return await factory()
      } else {
        return null
      }
    },
    staleTime: Infinity,
  })

  const createAccount = useMutation(api.createAccount(clientId))
  const createInitialRefreshToken = useMutation(api.createInitialRefreshToken())

  const token = curToken ?? createAccount.data ?? null

  const isMutating = useIsMutating({ mutationKey: ["auth"] })

  useEffect(() => {
    if (
      optionId &&
      !signInComponentQuery.isPending &&
      signInComponentQuery.data === null
    ) {
      // navigate back on error
      navigate(-1)
    }
  }, [optionId, signInComponentQuery.data, signInComponentQuery.status])

  return {
    step,
    api,
    tokenResponse: token,
    updating: isMutating > 0 || webAuthnAvailable.isPending,
    signInOptions: signInOptionsQuery.data ?? null,
    signInComponent: signInComponentQuery.data ?? null,
    async getAccount() {
      if (createAccount.isSuccess) {
        return createAccount.data
      }

      return await createAccount.mutateAsync()
    },
    selectOptionId(newOptionId) {
      setStep(SignInStep.signIn)
      navigate(loc, {
        state: { ...loc.state, signInOption: newOptionId },
        replace: !!optionId,
      })
    },
    completeSignIn(tokenResponse) {
      auth.authInfo = AuthInfo.createFromResponse(tokenResponse)
      if (optionId) {
        navigate(-1)
      }
    },
    completeRegistration(accessToken) {
      if (webAuthnAvailable.data == "platform") {
        setCurToken(accessToken)
        setStep(SignInStep.webAuthn)
        if (optionId) {
          navigate(-1)
        }
      } else {
        createInitialRefreshToken
          .mutateAsync(accessToken.access_token)
          .then((finalToken) => {
            auth.authInfo = AuthInfo.createFromResponse(finalToken)

            if (optionId) {
              navigate(-1)
            }
          })
          .then(() => {
            setStep(SignInStep.signIn)
            setCurToken(null)
            createAccount.reset()
          })
      }
    },
    completeWebAuthnRegistration(credentialId) {
      if (!token) {
        return
      }

      setSavedWebAuthnCredentialId(credentialId)
      createInitialRefreshToken
        .mutateAsync(token.access_token)
        .then((finalToken) => {
          auth.authInfo = AuthInfo.createFromResponse(finalToken)
        })
        .then(() => {
          setStep(SignInStep.signIn)
          setCurToken(null)
          createAccount.reset()
        })
    },
  }
}

/**
 * Get whether WebAuthn is available.
 */
export const getWebAuthnAvailability = async (): Promise<
  "platform" | boolean
> => {
  let available: "platform" | boolean = false
  if (browserSupportsWebAuthn()) {
    if (await platformAuthenticatorIsAvailable()) {
      available = "platform"
    } else {
      available = true
    }
  }
  return available
}
