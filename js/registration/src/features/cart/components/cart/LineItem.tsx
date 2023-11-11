import { Currency } from "#src/features/cart/components/cart/Currency"
import { Text, Title, useProps } from "@mantine/core"
import clsx from "clsx"
import { ReactNode } from "react"

export type LineItemProps = {
  name: string
  description?: string
  price: number
  modifiers?: ReactNode[]
  classNames?: {
    name?: string
    price?: string
    description?: string
  }
}

export const LineItem = (props: LineItemProps) => {
  const { name, price, description, modifiers, classNames } = useProps(
    "LineItem",
    {},
    props,
  )

  const descContent = description ? (
    <Text
      key="description"
      span
      className={clsx("LineItem-description", classNames?.description)}
    >
      {description}
    </Text>
  ) : null

  return [
    <Title
      key="name"
      order={5}
      className={clsx("LineItem-name", classNames?.name)}
    >
      {name}
    </Title>,
    <Text
      key="amount"
      component="span"
      className={clsx("LineItem-price", classNames?.price)}
    >
      <Currency amount={price} />
    </Text>,
    descContent,
    modifiers,
  ]
}
