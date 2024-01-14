import { useCheckoutAPI } from "#src/features/checkout/hooks"
import {
  Checkout,
  CheckoutContextValue,
  CheckoutState,
} from "#src/features/checkout/types/Checkout"
import { isAPIError } from "#src/utils/api"
import {
  useIsMutating,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"
import { ReactNode, createContext, useMemo, useState } from "react"

export const CheckoutProvider = ({
  checkoutId,
  children,
}: {
  checkoutId: string
  children?: ReactNode
}) => {
  const checkoutAPI = useCheckoutAPI()
  const client = useQueryClient()

  const checkoutQuery = useQuery({
    ...checkoutAPI.read(checkoutId),
    throwOnError: false,
  })

  const updateCount = useIsMutating({
    mutationKey: checkoutAPI.update(checkoutId).mutationKey,
  })

  const updateMutation = useMutation(checkoutAPI.update(checkoutId))
  const cancelMutation = useMutation(checkoutAPI.cancel(checkoutId))

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [completeMessage, setCompleteMessage] = useState<ReactNode>(undefined)

  const ctxValue = useMemo(() => {
    const ctx: CheckoutContextValue = {
      id: checkoutId,
      ...(checkoutQuery.isSuccess
        ? {
            ready: true,
            checkout: checkoutQuery.data,
          }
        : {
            ready: false,
            checkout: checkoutQuery.data,
          }),
      setSubmitting,
      error: error,
      setError: (error: string | null | undefined) => setError(error || null),
      updating: submitting || updateCount > 0,
      async update(body?: Record<string, unknown>) {
        setError(null)
        try {
          return await updateMutation.mutateAsync(body)
        } catch (e) {
          if (isAPIError(e)) {
            setError(e.json.detail)
          } else if (e instanceof Error) {
            setError(e.message)
          } else {
            setError(`${e}`)
          }
          throw e
        }
      },
      async cancel() {
        const cur = client.getQueryData<Checkout>(
          checkoutAPI.read(checkoutId).queryKey,
        )
        if (!cur || cur.state == CheckoutState.pending) {
          await cancelMutation.mutateAsync()
        }
      },
      completeMessage: completeMessage,
      setCompleteMessage(message) {
        setCompleteMessage(message)
      },
    }
    return ctx
  }, [
    checkoutId,
    checkoutQuery.isSuccess,
    checkoutQuery.data,
    updateCount,
    submitting,
    error,
    completeMessage,
  ])

  return (
    <CheckoutContext.Provider value={ctxValue}>
      {children}
    </CheckoutContext.Provider>
  )
}

export const CheckoutContext = createContext<CheckoutContextValue | null>(null)
