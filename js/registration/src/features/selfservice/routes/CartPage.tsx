import { Subtitle, Title } from "#src/components/title/Title"
import { fetchCartPricingResult } from "#src/features/cart/api"
import { useCurrentCartStore } from "#src/features/cart/hooks"
import { Cart } from "#src/features/cart/types"
import { Cart as CartComponent } from "#src/features/cart/components/cart/Cart"
import { useWretch } from "#src/hooks/api"
import { LineItem as LineItemComponent } from "#src/features/cart/components/cart/LineItem"
import { Modifier as ModifierComponent } from "#src/features/cart/components/cart/Modifier"
import { Anchor, Box, Button, Grid, Group, Stack, Text } from "@mantine/core"
import {
  IconAlertCircle,
  IconPlus,
  IconShoppingCart,
} from "@tabler/icons-react"
import { useLocation, useNavigate } from "#src/hooks/location"
import { observer } from "mobx-react-lite"
import { useLoader } from "#src/hooks/loader"
import { Loader } from "#src/util/loader"
import { CheckoutMethodsManager } from "#src/features/checkout/components/methods/CheckoutMethodsManager"
import { CheckoutManager } from "#src/features/checkout/components/checkout/CheckoutManager"
import { Fragment, useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useSelfServiceLoader } from "#src/features/selfservice/hooks"
import { Link as RLink } from "react-router-dom"
import { InterviewOptionsDialog } from "#src/features/cart/components/interview/InterviewOptionsDialog"
import { InterviewDialog } from "#src/features/interview/components/InterviewDialog"
import { CartRegistration } from "#src/features/cart/components/cart/CartRegistration"

import classes from "./CartPage.module.css"

export const CartPage = observer(() => {
  const { eventId = "" } = useParams()
  const currentCartStore = useCurrentCartStore()

  const [cartId, setCartId] = useState<string | null>(
    currentCartStore.currentCartId,
  )
  const [cart, setCart] = useState<Loader<Cart> | null>(currentCartStore.loader)

  useEffect(() => {
    if (!currentCartStore.currentCartId) {
      currentCartStore.checkAndSetCurrentCart()
    }
  }, [currentCartStore.currentCartId])

  useEffect(() => {
    if (currentCartStore.loader && currentCartStore.currentCartId) {
      setCart(currentCartStore.loader)
      setCartId(currentCartStore.currentCartId)
    }
  }, [currentCartStore.loader, currentCartStore.currentCartId])

  return (
    <Title title="Cart">
      <Subtitle subtitle="Your current shopping cart.">
        <Stack>
          <Box>
            <Anchor component={RLink} to={`/events/${eventId}`}>
              &laquo; Back to registrations
            </Anchor>
          </Box>
          {cart && cartId ? (
            <cart.Component placeholder={<CartViewPlaceholder />}>
              {(_cart) => (
                <CartView key={cartId} cartId={cartId} eventId={eventId} />
              )}
            </cart.Component>
          ) : (
            <CartViewPlaceholder />
          )}
        </Stack>
      </Subtitle>
    </Title>
  )
})

CartPage.displayName = "CartPage"

const CartViewPlaceholder = () => (
  <Title title="Cart">
    <Subtitle subtitle="Your current shopping cart.">
      <Stack>
        <CartComponent.Placeholder />
      </Stack>
    </Subtitle>
  </Title>
)

const CartView = observer(
  ({ cartId, eventId }: { cartId: string; eventId: string }) => {
    const wretch = useWretch()

    const selfService = useSelfServiceLoader()
    const loader = useLoader(() => {
      return Promise.all([selfService, fetchCartPricingResult(wretch, cartId)])
    })

    const loc = useLocation()
    const navigate = useNavigate()
    const currentCartStore = useCurrentCartStore()

    const [checkoutComplete, setCheckoutComplete] = useState(false)

    // hacky, redirect on dialog close when checkout is complete
    useEffect(() => {
      if (loc.state?.showCheckoutDialog?.cartId == null && checkoutComplete) {
        currentCartStore.clearCurrentCart()
        navigate(`/events/${eventId}`)
      }
    }, [loc.state?.showCheckoutDialog?.cartId, checkoutComplete])

    const showOptions = () => {
      navigate(loc, {
        state: {
          showCheckoutMethodsDialog: cartId,
        },
      })
    }

    const checkoutAvailable =
      !checkoutComplete &&
      loader.checkLoaded() &&
      loader.value[1].registrations.length > 0

    return (
      <loader.Component placeholder={<CartComponent.Placeholder />}>
        {([selfServiceResults, result]) => (
          <>
            {result.registrations.length > 0 ? (
              <CartComponent totalPrice={result.total_price}>
                {result.registrations.map((reg, i) => (
                  <Fragment key={reg.registration_id}>
                    {i != 0 && <CartComponent.Divider />}
                    <CartRegistration
                      name={reg.name ?? void 0}
                      onRemove={async () => {
                        const [newId, newCart] =
                          await currentCartStore.cartStore.removeRegistrationFromCart(
                            cartId,
                            reg.registration_id,
                          )
                        currentCartStore.setCurrentCart(newId, newCart)
                      }}
                    >
                      {reg.line_items.map((li, i) => (
                        <LineItemComponent
                          key={i}
                          name={li.name}
                          description={li.description}
                          price={li.price}
                          modifiers={li.modifiers.map((m, i) => (
                            <ModifierComponent
                              key={i}
                              name={m.name}
                              amount={m.amount}
                            />
                          ))}
                        />
                      ))}
                    </CartRegistration>
                  </Fragment>
                ))}
              </CartComponent>
            ) : (
              <EmptyCartView />
            )}
            <Grid>
              {selfServiceResults.add_options.length > 0 && (
                <Grid.Col span={{ base: 12, sm: "content" }}>
                  <Button
                    variant="outline"
                    leftSection={<IconPlus />}
                    fullWidth
                    onClick={() => {
                      // show dialog
                      navigate(loc, {
                        state: {
                          ...loc.state,
                          showInterviewOptionsDialog: eventId,
                        },
                      })
                    }}
                  >
                    Add Registration
                  </Button>
                </Grid.Col>
              )}
              {checkoutAvailable && (
                <Grid.Col span={{ base: 12, sm: "content" }}>
                  <Button
                    variant="filled"
                    leftSection={<IconShoppingCart />}
                    fullWidth
                    onClick={() => showOptions()}
                  >
                    Checkout
                  </Button>
                </Grid.Col>
              )}
            </Grid>
            <CheckoutMethodsManager cartId={cartId} />
            <CheckoutManager
              cartId={cartId}
              onComplete={() => {
                setCheckoutComplete(true)

                // reload self-service memberships
                selfService.fetch()
              }}
            />
            <InterviewOptionsDialog.Manager
              options={selfServiceResults.add_options}
            />
            <InterviewDialog.Manager
              onComplete={async (record) => {
                const response = record.stateResponse
                const metadata = record.metadata

                if (
                  metadata.cartId &&
                  metadata.eventId &&
                  response.complete &&
                  response.target_url
                ) {
                  const res = await wretch
                    .url(response.target_url, true)
                    .json({ state: response.state })
                    .post()
                    .res()

                  const cart: Cart = await res.json()

                  const url = new URL(res.url)
                  const parts = url.pathname.split("/")
                  const newCartId = parts[parts.length - 1]
                  currentCartStore.setCurrentCart(newCartId, cart)
                  navigate(loc, {
                    state: { ...loc.state, showInterviewDialog: undefined },
                    replace: true,
                  })
                  navigate(`/events/${metadata.eventId}/cart`)
                }
              }}
            />
          </>
        )}
      </loader.Component>
    )
  },
)

CartView.displayName = "CartView"

const EmptyCartView = () => (
  <Box className={classes.emptyCart}>
    <Text c="dimmed" component="div">
      <Group align="center">
        <IconAlertCircle />
        <Text span inline>
          Your cart is empty.
        </Text>
      </Group>
    </Text>
  </Box>
)
