import { CheckoutAPIContext } from "#src/features/checkout/api"
import { CheckoutDialog } from "#src/features/checkout/components/checkout/CheckoutDialog"
import { MockCheckoutComponent } from "#src/features/checkout/impl/mock/MockCheckoutComponent"
import { Checkout, CheckoutState } from "#src/features/checkout/types/Checkout"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { useNavigate } from "#src/hooks/location"
import { Button } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"
import { MemoryRouter, Route, Routes } from "react-router-dom"

const meta: Meta<typeof MockCheckoutComponent> = {
  component: MockCheckoutComponent,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta

const wait = async () => await new Promise((r) => window.setTimeout(r, 1500))

export const Default: StoryObj<typeof MockCheckoutComponent> = {
  decorators: [
    (Story) => (
      <MemoryRouter>
        <Routes>
          <Route path="*" element={<Story />} />
        </Routes>
      </MemoryRouter>
    ),
  ],
  render() {
    const navigate = useNavigate()
    const [client] = useState(() => new QueryClient())

    const [mockAPI] = useState(() => ({
      state: CheckoutState.pending,
      read(checkoutId: string) {
        return {
          queryKey: ["checkouts", checkoutId],
          queryFn: async () => {
            await wait()

            return {
              cartId: null,
              data: {},
              externalId: `mock-${checkoutId}`,
              id: `${checkoutId}`,
              method: null,
              service: "mock",
              state: this.state,
            }
          },
          staleTime: Infinity,
        }
      },
      update(checkoutId: string) {
        return {
          mutationFn: async (body?: Record<string, unknown>) => {
            await wait()
            let num = parseInt(body?.card as string)
            if (isNaN(num)) {
              num = 0
            }

            if (!num) {
              throw new Error("Invalid card")
            }

            this.state = CheckoutState.complete
            return {
              cartId: null,
              data: body,
              externalId: `mock-${checkoutId}`,
              id: `${checkoutId}`,
              method: null,
              service: "mock",
              state: this.state,
            }
          },
          onSuccess: (value: Checkout) => {
            client.setQueryData(this.read(checkoutId).queryKey, value)
          },
        }
      },
      cancel(checkoutId: string) {
        return {
          mutationFn: async () => {
            await wait()
            this.state = CheckoutState.canceled
            return null
          },
          onSuccess: () => {
            client.setQueryData(
              this.read(checkoutId).queryKey,
              (old: Checkout | undefined): Checkout | undefined =>
                old ? { ...old, state: CheckoutState.canceled } : undefined,
            )
          },
        }
      },
    }))

    return (
      <QueryClientProvider client={client}>
        <CheckoutAPIContext.Provider value={mockAPI as unknown as CheckoutAPI}>
          <Button
            m="1rem"
            onClick={() =>
              navigate(window.location, {
                state: {
                  showCheckoutDialog: {
                    cartId: "1",
                    checkoutId: "1",
                    service: "mock",
                  },
                },
              })
            }
          >
            Checkout
          </Button>
          <CheckoutDialog.Manager />
          {/* <ModalDialog
            opened
            onClose={() => {}}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "stretch",
            }}
          >
            <CheckoutComponent checkoutId="1">
              {(renderProps) => (
                <>
                  <Box style={{ flex: "auto" }}>
                    <MockCheckoutComponent
                      {...(renderProps as CheckoutRenderProps<"mock">)}
                    />
                  </Box>
                  {renderProps.error && (
                    <Text c="red" mt="1rem">
                      {renderProps.error}
                    </Text>
                  )}
                  <LoadingOverlay visible={renderProps.isLoading} />
                </>
              )}
            </CheckoutComponent>
          </ModalDialog> */}
        </CheckoutAPIContext.Provider>
      </QueryClientProvider>
    )
  },
}
