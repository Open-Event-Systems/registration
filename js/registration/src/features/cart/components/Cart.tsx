import { Currency } from "#src/features/cart/components/Currency.js"
import {
  Box,
  BoxProps,
  DefaultProps,
  Divider,
  DividerProps,
  Selectors,
  Skeleton,
  Text,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { ReactNode } from "react"

const cartStyles = createStyles((theme) => ({
  root: {
    display: "grid",
    gridTemplateColumns:
      "[icon-start] auto [icon-end item-name-start item-description-start] 1fr [item-name-end item-description-end item-amount-start] auto [item-amount-end]",
    justifyItems: "end",
    alignItems: "baseline",
    columnGap: 16,
    [`@media (max-width: ${theme.breakpoints.xs})`]: {
      gridTemplateColumns:
        "[icon-start] auto [icon-end item-name-start item-description-start item-amount-start] 1fr [item-name-end item-description-end item-amount-end]",
      columnGap: 8,
    },
  },
  totalText: {
    marginTop: theme.spacing.sm,
    gridColumn: "item-name-start / item-name-end",
    textAlign: "right",
    fontWeight: "bold",
  },
  total: {
    gridColumn: "item-amount-start / item-amount-end",
    textAlign: "right",
    fontWeight: "bold",
    fontSize: "x-large",
  },
  divider: {
    gridColumn: "1 / -1",
    justifySelf: "stretch",
    marginTop: theme.spacing.sm,
  },
  placeholder: {
    display: "grid",
    gridTemplateColumns: "20px 1fr 50px",
    justifyItems: "end",
    alignItems: "baseline",
    columnGap: 16,
    rowGap: 8,
  },
  skeleton: {},
}))

export type CartProps = {
  children?: ReactNode
  totalPrice: number
} & BoxProps &
  DefaultProps<Selectors<typeof cartStyles>>

export const Cart = (props: CartProps) => {
  const {
    className,
    classNames,
    styles,
    unstyled,
    children,
    totalPrice,
    ...other
  } = useComponentDefaultProps("Cart", {}, props)

  const { classes, cx } = cartStyles(undefined, {
    name: "Cart",
    classNames,
    styles,
    unstyled,
  })

  return (
    <Box className={cx(classes.root, className)} {...other}>
      {children}
      <CartDivider />
      <Text span className={classes.totalText}>
        Total
      </Text>
      <Text span className={classes.total}>
        <Currency amount={totalPrice} />
      </Text>
    </Box>
  )
}

const CartDivider = (
  props: Omit<DividerProps, "styles"> &
    DefaultProps<Selectors<typeof cartStyles>>
) => {
  const { className, classNames, styles, unstyled, ...other } = props

  const { classes, cx } = cartStyles(void 0, {
    name: "Cart",
    classNames,
    styles,
    unstyled,
  })

  return <Divider className={cx(classes.divider, className)} {...other} />
}

Cart.Divider = CartDivider

type CartPlaceholderProps = Omit<BoxProps, "children"> &
  DefaultProps<Selectors<typeof cartStyles>>

const CartPlaceholder = (props: CartPlaceholderProps) => {
  const { className, classNames, styles, unstyled, ...other } = props

  const { classes, cx } = cartStyles(void 0, {
    name: "Cart",
    classNames,
    styles,
    unstyled,
  })

  return (
    <Box className={cx(classes.placeholder, className)} {...other}>
      <Skeleton className={classes.skeleton} height={24} />
      <Skeleton
        className={classes.skeleton}
        height={24}
        width={250}
        sx={{ justifySelf: "start" }}
      />

      <Skeleton
        className={classes.skeleton}
        height={16}
        width={150}
        sx={{ gridColumn: "-3 / -2" }}
      />
      <Skeleton
        className={classes.skeleton}
        height={16}
        sx={{ gridColumn: "-2 / -1" }}
      />

      <Skeleton
        className={classes.skeleton}
        height={16}
        width={150}
        sx={{ gridColumn: "-3 / -2" }}
      />
      <Skeleton
        className={classes.skeleton}
        height={16}
        sx={{ gridColumn: "-2 / -1" }}
      />

      <Cart.Divider />

      <Skeleton className={classes.skeleton} height={24} />
      <Skeleton
        className={classes.skeleton}
        height={24}
        width={250}
        sx={{ justifySelf: "start" }}
      />

      <Skeleton
        className={classes.skeleton}
        height={16}
        width={150}
        sx={{ gridColumn: "-3 / -2" }}
      />
      <Skeleton
        className={classes.skeleton}
        height={16}
        sx={{ gridColumn: "-2 / -1" }}
      />

      <Skeleton
        className={classes.skeleton}
        height={16}
        width={150}
        sx={{ gridColumn: "-3 / -2" }}
      />
      <Skeleton
        className={classes.skeleton}
        height={16}
        sx={{ gridColumn: "-2 / -1" }}
      />
    </Box>
  )
}

Cart.Placeholder = CartPlaceholder
