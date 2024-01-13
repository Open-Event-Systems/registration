import { useCartAPI } from "#src/features/cart/hooks"
import { Search } from "#src/features/checkout/components/search/Search"
import { useCheckoutAPI } from "#src/features/checkout/hooks"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { action, observable } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { Fragment, useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { Cart as CartComponent } from "#src/features/cart/components/cart/Cart"
import { LineItem as LineItemComponent } from "#src/features/cart/components/cart/LineItem"
import { Modifier as ModifierComponent } from "#src/features/cart/components/cart/Modifier"
import { CartRegistration } from "#src/features/cart/components/cart/CartRegistration"
import { Box, Button, Grid, Group, Text } from "@mantine/core"
import { IconAlertCircle, IconShoppingCart } from "@tabler/icons-react"
import { InterviewDialog } from "#src/features/interview"
import { CheckoutManager } from "#src/features/checkout/components/checkout/CheckoutManager"
import { useLocation, useNavigate } from "#src/hooks/location"

import classes from "./CheckoutCartPage.module.css"

export const CheckoutCartPage = observer(() => {
  const { cartId = "" } = useParams()

  const loc = useLocation()
  const navigate = useNavigate()

  const cartAPI = useCartAPI()
  const cart = useQuery({
    ...cartAPI.readCart(cartId),
  })
  const pricingResult = useQuery({
    ...cartAPI.readPricingResult(cartId),
    enabled: cart.isSuccess,
  })
  const [checkoutComplete, setCheckoutComplete] = useState(false)

  const removeRegistration = useMutation(
    cartAPI.removeRegistrationFromCart(cartId),
  )

  if (!pricingResult.isSuccess) {
    return <CartComponent.Placeholder />
  }

  const checkoutAvailable =
    !checkoutComplete && pricingResult.data.registrations.length > 0

  const showOptions = () => {
    navigate(loc, {
      state: {
        showCheckoutDialog: {
          cartId: cartId,
        },
      },
    })
  }

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
                  const [newId] = await removeRegistration.mutateAsync(
                    reg.registration_id,
                  )
                  navigate(`/checkouts/cart/${newId}`)
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
      <CheckoutManager
        onComplete={() => {
          setCheckoutComplete(true)
          navigate(`/checkouts`)
        }}
      />
    </>
  )
})

CheckoutCartPage.displayName = "CheckoutCartPage"

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
