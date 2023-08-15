import { Currency } from "#src/features/cart/components/Currency.js"
import {
  DefaultProps,
  Selectors,
  Text,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"

const modifierStyles = createStyles({
  text: {
    gridColumn: "item-name-start / item-name-end",
    textAlign: "right",
    fontSize: "small",
  },
  amount: {
    gridColumn: "item-amount-start / item-amount-end",
    textAlign: "right",
    fontSize: "small",
  },
})

export type ModifierProps = {
  name: string
  amount: number
} & Omit<DefaultProps<Selectors<typeof modifierStyles>>, "className">

/**
 * Line item modifier.
 */
export const Modifier = (props: ModifierProps) => {
  const { classNames, styles, unstyled, name, amount } =
    useComponentDefaultProps("Modifier", {}, props)

  const { classes } = modifierStyles(undefined, {
    name: "Modifier",
    classNames,
    styles,
    unstyled,
  })

  return [
    <Text key="name" component="span" className={classes.text}>
      {name}
    </Text>,
    <Text key="amount" component="span" className={classes.amount}>
      <Currency amount={amount} />
    </Text>,
  ]
}
