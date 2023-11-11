import { Currency } from "#src/features/cart/components/cart/Currency"
import { Text, useProps } from "@mantine/core"
import clsx from "clsx"

export type ModifierProps = {
  name: string
  amount: number
  classNames?: {
    text?: string
    amount?: string
  }
}

/**
 * Line item modifier.
 */
export const Modifier = (props: ModifierProps) => {
  const { name, amount, classNames } = useProps("Modifier", {}, props)

  return [
    <Text
      key="name"
      component="span"
      className={clsx("Modifier-text", classNames?.text)}
    >
      {name}
    </Text>,
    <Text
      key="amount"
      component="span"
      className={clsx("Modifier-amount", classNames?.amount)}
    >
      <Currency amount={amount} />
    </Text>,
  ]
}
