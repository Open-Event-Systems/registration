import { placeholderWretch } from "#src/config/api"
import { getCartIdFromResponse } from "#src/features/cart/api"
import { useCartAPI } from "#src/features/cart/hooks"
import { Cart } from "#src/features/cart/types"
import { setCurrentCartId } from "#src/features/cart/utils"
import { useInterviewRecordStore } from "#src/features/interview"
import {
  SelfServiceAPIContext,
  checkAccessCode,
  listSelfServiceRegistrations,
} from "#src/features/selfservice/api"
import { SelfServiceAPI } from "#src/features/selfservice/types"
import { useWretch } from "#src/hooks/api"
import { useLocation, useNavigate } from "#src/hooks/location"
import { isNotFoundError } from "#src/utils/api"
import { createLoader } from "#src/utils/loader"
import {
  InterviewStateRecord,
  defaultAPI,
  startInterview,
} from "@open-event-systems/interview-lib"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createContext, useCallback, useContext, useEffect } from "react"

export const SelfServiceLoaderContext = createContext(
  createLoader(() => listSelfServiceRegistrations(placeholderWretch)),
)

export const useSelfServiceLoader = () => useContext(SelfServiceLoaderContext)

export const AccessCodeLoaderContext = createContext(
  createLoader(() => checkAccessCode(placeholderWretch, "", "")),
)

export const useAccessCodeLoader = () => useContext(AccessCodeLoaderContext)

export const useSelfServiceAPI = (): SelfServiceAPI =>
  useContext(SelfServiceAPIContext)

/**
 * Get a query for the current cart.
 * @param eventId - the event ID
 */
export const useCurrentCart = (eventId: string) => {
  const api = useCartAPI()
  const currentCartQuery = useQuery({
    ...api.readCurrentCart(eventId),
    throwOnError: false,
  })
  const currentCartError =
    (currentCartQuery.isError && isNotFoundError(currentCartQuery.error)) ||
    (currentCartQuery.isSuccess && currentCartQuery.data == null)

  const emptyCartQuery = useQuery({
    ...api.readEmptyCart(eventId),
    enabled: currentCartError,
  })
  const setCurrentCart = useMutation(api.setCurrentCart(eventId))

  useEffect(() => {
    if (currentCartError && emptyCartQuery.data) {
      setCurrentCart.mutate(emptyCartQuery.data)
    }
  }, [currentCartError, emptyCartQuery.data, setCurrentCart])

  return currentCartQuery
}

type StartCartInterviewFn = (
  interviewId: string,
  options?: {
    accessCode?: string
    registrationId?: string
  },
) => Promise<void>

/**
 * Get a function that starts an interview to change a cart.
 * @param cartId - the cart ID
 * @param eventId - the event ID
 */
export const useStartCartInterviewFn = (
  cartId: string,
  eventId: string,
): StartCartInterviewFn => {
  const client = useQueryClient()
  const recordStore = useInterviewRecordStore()
  const cartAPI = useCartAPI()
  const navigate = useNavigate()
  const loc = useLocation()

  const startFn: StartCartInterviewFn = async (interviewId, options = {}) => {
    const state = await client.fetchQuery(
      cartAPI.readAddInterview(cartId, interviewId, options),
    )
    const record = await startInterview(recordStore, defaultAPI, state, {
      eventId: eventId,
      cartId: cartId,
    })
    navigate(loc, {
      state: {
        ...loc.state,
        accessCodeDialogRegistrationId: undefined,
        showInterviewOptionsDialog: undefined,
        showInterviewDialog: {
          eventId: eventId,
          recordId: record.id,
        },
      },
    })
  }

  return useCallback(startFn, [
    cartId,
    eventId,
    client,
    recordStore,
    cartAPI,
    navigate,
    loc,
  ])
}

type CompleteCartInterviewFn = (record: InterviewStateRecord) => Promise<void>

/**
 * Get a function that handles a completed cart interview and redirects to the updated cart.
 */
export const useCompleteCartInterviewFn = (): CompleteCartInterviewFn => {
  const client = useQueryClient()
  const cartAPI = useCartAPI()
  const navigate = useNavigate()
  const loc = useLocation()
  const wretch = useWretch()

  const func: CompleteCartInterviewFn = async (record) => {
    const stateResponse = record.stateResponse
    const { cartId, eventId } = record.metadata

    if (
      cartId &&
      eventId &&
      stateResponse.complete &&
      stateResponse.target_url
    ) {
      const res = await wretch
        .url(stateResponse.target_url, true)
        .json({ state: stateResponse.state })
        .post()
        .res()

      const newCartId = getCartIdFromResponse(res)
      const newCart: Cart = await res.json()

      // update the current cart ID
      setCurrentCartId(eventId, newCartId)

      // store the returned cart
      client.setQueryData(cartAPI.readCart(newCartId).queryKey, [
        newCartId,
        newCart,
      ])

      // update the current cart query
      client.setQueryData(cartAPI.readCurrentCart(eventId).queryKey, [
        newCartId,
        newCart,
      ])

      navigate(loc, {
        state: { ...loc.state, showInterviewDialog: undefined },
        replace: true,
      })
      navigate(`/events/${eventId}/cart`)
    }
  }

  return useCallback(func, [client, cartAPI, navigate, loc, wretch])
}
