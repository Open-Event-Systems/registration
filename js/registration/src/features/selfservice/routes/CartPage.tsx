import { Subtitle, Title } from "#src/components/title/Title"
import { useCartAPI } from "#src/features/cart/hooks"
import { Cart as CartComponent } from "#src/features/cart/components/cart/Cart"
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
import { CheckoutMethodsManager } from "#src/features/checkout/components/methods/CheckoutMethodsManager"
import { CheckoutManager } from "#src/features/checkout/components/checkout/CheckoutManager"
import { Fragment, useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import {
  useCompleteCartInterviewFn,
  useSelfServiceAPI,
} from "#src/features/selfservice/hooks"
import { Link as RLink } from "react-router-dom"
import { InterviewOptionsDialog } from "#src/features/cart/components/interview/InterviewOptionsDialog"
import { InterviewDialog } from "#src/features/interview/components/InterviewDialog"
import { CartRegistration } from "#src/features/cart/components/cart/CartRegistration"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { setCurrentCartId } from "#src/features/cart/utils"

import classes from "./CartPage.module.css"
import { isNotFoundError } from "#src/utils/api"

export const CartPage = observer(() => {
  const { eventId = "" } = useParams()

  const cartAPI = useCartAPI()
  const currentCart = useQuery({
    ...cartAPI.readCurrentCart(eventId),
    throwOnError: false,
  })

  const currentCartFailed =
    (currentCart.isError && isNotFoundError(currentCart.error)) ||
    (currentCart.isSuccess && currentCart.data == null)

  const emptyCart = useQuery({
    ...cartAPI.readEmptyCart(eventId),
    enabled: currentCartFailed,
  })
  const setCurrentCart = useMutation(cartAPI.setCurrentCart(eventId))

  // replace current cart with empty cart if not found
  useEffect(() => {
    if (currentCartFailed && emptyCart.data) {
      setCurrentCart.mutate(emptyCart.data)
    }
  }, [currentCartFailed, emptyCart.data])

  if (!currentCart.isSuccess || !currentCart.data) {
    return <CartViewPlaceholder />
  }

  const currentCartId = currentCart.data[0]

  return (
    <Title title="Cart">
      <Subtitle subtitle="Your current shopping cart.">
        <Stack>
          <Box>
            <Anchor component={RLink} to={`/events/${eventId}`}>
              &laquo; Back to registrations
            </Anchor>
          </Box>
          <CartView
            key={currentCartId}
            cartId={currentCartId}
            eventId={eventId}
          />
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
    const selfServiceAPI = useSelfServiceAPI()
    const cartAPI = useCartAPI()

    const client = useQueryClient()
    const pricingResult = useQuery(cartAPI.readPricingResult(cartId))
    const selfService = useQuery(
      selfServiceAPI.listRegistrations({ eventId: eventId }),
    )
    const removeRegistration = useMutation(
      cartAPI.removeRegistrationFromCart(cartId),
    )
    const setCurrentCart = useMutation(cartAPI.setCurrentCart(eventId))

    const loc = useLocation()
    const navigate = useNavigate()

    const completeInterview = useCompleteCartInterviewFn()

    const [checkoutComplete, setCheckoutComplete] = useState(false)

    // hacky, redirect on dialog close when checkout is complete
    useEffect(() => {
      if (loc.state?.showCheckoutDialog?.cartId == null && checkoutComplete) {
        setCurrentCartId(eventId, "")
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

    if (!pricingResult.isSuccess || !selfService.isSuccess) {
      return <CartComponent.Placeholder />
    }

    const checkoutAvailable =
      !checkoutComplete && pricingResult.data.registrations.length > 0

    return (
      <>
        {pricingResult.data.registrations.length > 0 ? (
          <CartComponent totalPrice={pricingResult.data.total_price}>
            {pricingResult.data.registrations.map((reg, i) => (
              <Fragment key={reg.registration_id}>
                {i != 0 && <CartComponent.Divider />}
                <CartRegistration
                  name={reg.name ?? void 0}
                  onRemove={async () => {
                    const [newId, newCart] =
                      await removeRegistration.mutateAsync(reg.registration_id)
                    setCurrentCart.mutate([newId, newCart])
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
          {selfService.data.add_options.length > 0 && (
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
                      showInterviewOptionsDialog: {
                        eventId: eventId,
                        cartId: cartId,
                      },
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
            client.invalidateQueries({
              queryKey: ["self-service", "registrations"],
            })
          }}
        />
        <InterviewOptionsDialog.Manager
          options={selfService.data.add_options}
        />
        <InterviewDialog.Manager onComplete={completeInterview} />
      </>
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
