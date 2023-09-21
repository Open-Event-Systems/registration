import { Currency } from "#src/features/cart/components/Currency.js"
import {
  DefaultProps,
  Selectors,
  Text,
  Title,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { ReactNode } from "react"

const lineItemStyles = createStyles((theme) => ({
  name: {
    gridColumn: "item-name-start / item-name-end",
    fontWeight: "bold",
    fontSize: "large",
    textAlign: "right",
    marginTop: theme.spacing.xs,
  },
  price: {
    gridColumn: "item-amount-start / item-amount-end",
    display: "block",
    fontWeight: "bold",
    fontSize: "large",
    textAlign: "right",
  },
  description: {
    gridColumn: "item-description-start / item-description-end",
    textAlign: "right",
  },
}))

export type LineItemProps = {
  name: string
  description?: string
  price: number
  modifiers?: ReactNode[]
} & Omit<DefaultProps<Selectors<typeof lineItemStyles>>, "className">

export const LineItem = (props: LineItemProps) => {
  const { name, price, description, modifiers, classNames, styles, unstyled } =
    useComponentDefaultProps("LineItem", {}, props)

  const { classes } = lineItemStyles(undefined, {
    name: "LineItem",
    classNames,
    styles,
    unstyled,
  })

  const descContent = description ? (
    <Text key="description" span className={classes.description}>
      {description}
    </Text>
  ) : null

  return [
    <Title key="name" order={5} className={classes.name}>
      {name}
    </Title>,
    <Text key="amount" component="span" className={classes.price}>
      <Currency amount={price} />
    </Text>,
    descContent,
    modifiers,
  ]
}
