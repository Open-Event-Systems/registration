import { Currency } from "#src/features/cart/components/Currency.js"
import {
  ComponentPropsWithoutRef,
  ElementType,
  ReactNode,
  useEffect,
  useState,
} from "react"
import QRCode from "qrcode"
import type { CSSObject } from "@mantine/core"

export const receiptClassNames = {
  table: "receipt-table",
  header: "receipt-header",
  headerRow: "receipt-header-row",
  title: "receipt-title",
  date: "receipt-date",
  receiptId: "receipt-id",
  registration: "receipt-registration-body",
  registrationRow: "receipt-registration-row",
  name: "receipt-registration-name",
  code: "receipt-registration-code",
  codeImg: "receipt-code",
  codeImgLoading: "receipt-code-loading",
  lineItem: "receipt-line-item-row",
  lineItemName: "receipt-line-item-name",
  lineItemAmount: "receipt-line-item-amount",
  lineItemDescriptionRow: "line-item-description-row",
  description: "receipt-line-item-description",
  descriptionSpacer: "receipt-line-item-description-spacer",
  modifierRow: "receipt-modifier-row",
  modifierName: "receipt-modifier-name",
  modifierAmount: "receipt-modifier-amount",
  divider: "receipt-divider",
  footer: "receipt-footer",
  footerRow: "receipt-footer-row",
  totalName: "receipt-total-name",
  totalAmount: "receipt-total-amount",
}

const receiptStylesMap: CSSObject = {
  [receiptClassNames.table]: {
    display: "grid",
    gridTemplateColumns:
      "[name-start code-start] auto [code-end item-name-start item-description-start] 1fr [item-name-end item-description-end item-amount-start] auto [item-amount-end name-end]",
    columnGap: 8,
    ["@media (max-width: 48em)"]: {
      gridTemplateColumns:
        "[name-start code-start] auto [item-name-start item-description-start] 1fr [item-name-end item-description-end item-amount-start] auto [item-amount-end name-end code-end]",
    },
  },
  [receiptClassNames.header]: {
    display: "contents",
  },
  [receiptClassNames.headerRow]: {
    display: "contents",
  },
  [receiptClassNames.title]: {
    fontSize: "1.5rem",
    fontWeight: "bold",
    gridColumn: "name",
    textAlign: "left",
  },
  [receiptClassNames.receiptId]: {
    fontSize: "1.5rem",
    fontFamily: "monospace",
    fontWeight: "normal",
  },
  [receiptClassNames.date]: {
    fontWeight: "normal",
    gridColumn: "name",
    textAlign: "left",
  },
  [receiptClassNames.registration]: {
    display: "contents",
  },
  [receiptClassNames.registrationRow]: {
    display: "contents",
  },
  [receiptClassNames.name]: {
    gridColumn: "name",
    fontSize: "1.25rem",
    fontWeight: "bold",
    marginTop: 16,
    marginBottom: 8,
  },
  [receiptClassNames.code]: {
    gridColumn: "code",
    gridRow: "span 10",
    justifySelf: "center",
  },
  [receiptClassNames.codeImg]: {
    width: 150,
    height: 150,
  },
  [receiptClassNames.codeImgLoading]: {
    visibility: "hidden",
  },
  [receiptClassNames.lineItem]: {
    display: "contents",
  },
  [receiptClassNames.lineItemName]: {
    gridColumn: "item-name",
    fontWeight: "bold",
    textAlign: "right",
  },
  [receiptClassNames.lineItemAmount]: {
    gridColumn: "item-amount",
    fontWeight: "bold",
    textAlign: "right",
  },
  [receiptClassNames.lineItemDescriptionRow]: {
    display: "contents",
  },
  [receiptClassNames.description]: {
    gridColumn: "item-description",
    textAlign: "right",
    fontSize: "0.75rem",
  },
  [receiptClassNames.descriptionSpacer]: {
    gridColumn: "item-amount",
  },
  [receiptClassNames.modifierRow]: {
    display: "contents",
  },
  [receiptClassNames.modifierName]: {
    gridColumn: "item-name",
    textAlign: "right",
    fontSize: "0.75rem",
  },
  [receiptClassNames.modifierAmount]: {
    gridColumn: "item-amount",
    textAlign: "right",
    fontSize: "0.75rem",
  },
  [receiptClassNames.divider]: {
    borderBottom: "#ccc solid 1px",
    gridColumn: "name",
    height: 0,
    marginTop: 8,
    marginBottom: 8,
  },
  [receiptClassNames.footer]: {
    display: "contents",
  },
  [receiptClassNames.footerRow]: {
    display: "contents",
  },
  [receiptClassNames.totalName]: {
    gridColumn: "item-name",
    fontSize: "1.25rem",
    fontWeight: "bold",
    textAlign: "right",
  },
  [receiptClassNames.totalAmount]: {
    gridColumn: "item-amount",
    fontSize: "1.25rem",
    fontWeight: "bold",
    textAlign: "right",
  },
}

export const receiptStyles: CSSObject = {}

Object.entries(receiptStylesMap).forEach(([className, styles]) => {
  receiptStyles[`.${className}`] = styles
})

type ReceiptStyleProps<T extends ElementType> = {
  classes?: Partial<typeof receiptClassNames>
} & ComponentPropsWithoutRef<T>

export type ReceiptProps = {
  receiptId: string
  date?: string
  totalPrice: number
  children?: ReactNode
} & ReceiptStyleProps<"table">

export const Receipt = (props: ReceiptProps) => {
  const {
    receiptId,
    date,
    totalPrice,
    className,
    classes,
    style,
    children,
    ...other
  } = props

  return (
    <table
      className={getClasses(classes, "table", className)}
      style={{
        ...style,
      }}
      {...other}
    >
      <thead className={getClasses(classes, "header")}>
        <tr className={getClasses(classes, "headerRow")}>
          <th scope="col" colSpan={3} className={getClasses(classes, "title")}>
            Receipt{" "}
            <span className={getClasses(classes, "receiptId")}>
              {receiptId}
            </span>
          </th>
        </tr>
        {date && (
          <tr className={getClasses(classes, "headerRow")}>
            <th scope="col" colSpan={3} className={getClasses(classes, "date")}>
              {date}
            </th>
          </tr>
        )}
      </thead>
      {children}
      <tfoot className={getClasses(classes, "footer")}>
        <tr className={getClasses(classes, "footerRow")}>
          <td colSpan={2} className={getClasses(classes, "totalName")}>
            Total
          </td>
          <td className={getClasses(classes, "totalAmount")}>
            <Currency amount={totalPrice} />
          </td>
        </tr>
      </tfoot>
    </table>
  )
}

export type ReceiptRegistrationProps = {
  name?: string
  receiptUrl?: string
} & ReceiptStyleProps<"tbody">

const ReceiptRegistration = (props: ReceiptRegistrationProps) => {
  const { name, receiptUrl, className, classes, children, ...other } = props

  return (
    <tbody
      className={getClasses(classes, "registration", className)}
      {...other}
    >
      <tr className={getClasses(classes, "registrationRow")}>
        <td className={getClasses(classes, "name")} colSpan={3}>
          {name || "Registration"}
        </td>
      </tr>
      {receiptUrl && (
        <tr className={getClasses(classes, "registrationRow")}>
          <td className={getClasses(classes, "code")} colSpan={3}>
            <ReceiptCode receiptUrl={receiptUrl} classes={classes} />
          </td>
        </tr>
      )}
      {children}
    </tbody>
  )
}

Receipt.Registration = ReceiptRegistration

export type ReceiptCodeProps = {
  receiptUrl: string
} & ReceiptStyleProps<"img">

const ReceiptCode = (props: ReceiptCodeProps) => {
  const { receiptUrl, className, classes, ...other } = props

  const [dataURL, setDataURL] = useState<string | undefined>(undefined)

  useEffect(() => {
    makeCode(receiptUrl).then((dataURL) => {
      setDataURL(dataURL)
    })
  }, [receiptUrl])

  return (
    <img
      className={getClasses(
        classes,
        "codeImg",
        className,
        !dataURL
          ? classes?.codeImgLoading || receiptClassNames.codeImgLoading
          : void 0
      )}
      src={dataURL}
      alt=""
      {...other}
    />
  )
}

const makeCode = (url: string): Promise<string> => {
  const urlObj = new URL(url, window.location.href)
  const hostPart = `${urlObj.protocol}//${urlObj.host}`
  const pathParts = urlObj.pathname.split("/")
  const pathPrefix = pathParts.slice(0, pathParts.length - 1).join("/") + "/"
  const id = pathParts[pathParts.length - 1]
  const fragment = urlObj.hash
  return QRCode.toDataURL([
    {
      data: hostPart.toUpperCase(),
      mode: "alphanumeric",
    },
    {
      data: pathPrefix,
    },
    {
      data: id.toUpperCase(),
      mode: "alphanumeric",
    },
    ...(fragment ? [{ data: fragment }] : []),
  ])
}

Receipt.Code = ReceiptCode

export type ReceiptLineItemProps = {
  name: string
  description?: string
  price: number
} & ReceiptStyleProps<"tr">

const ReceiptLineItem = (props: ReceiptLineItemProps) => {
  const { name, description, price, className, classes, children, ...other } =
    props

  return [
    <tr
      key="name"
      className={getClasses(classes, "lineItem", className)}
      {...other}
    >
      <td colSpan={2} className={getClasses(classes, "lineItemName")}>
        {name}
      </td>
      <td className={getClasses(classes, "lineItemAmount")}>
        <Currency amount={price} />
      </td>
    </tr>,
    description ? (
      <tr
        key="description"
        className={getClasses(classes, "lineItemDescriptionRow")}
      >
        <td colSpan={2} className={getClasses(classes, "description")}>
          {description}
        </td>
        <td className={getClasses(classes, "descriptionSpacer")}></td>
      </tr>
    ) : null,
    children,
  ]
}

Receipt.LineItem = ReceiptLineItem

export type ReceiptModifierProps = {
  name: string
  amount: number
} & Omit<ReceiptStyleProps<"tr">, "children">

const ReceiptModifier = (props: ReceiptModifierProps) => {
  const { name, amount, className, classes, ...other } = props

  return (
    <tr className={getClasses(classes, "modifierRow", className)} {...other}>
      <td colSpan={2} className={getClasses(classes, "modifierName")}>
        {name}
      </td>
      <td className={getClasses(classes, "modifierAmount")}>
        <Currency amount={amount} />
      </td>
    </tr>
  )
}

Receipt.Modifier = ReceiptModifier

export type ReceiptDividerProps = Omit<ReceiptStyleProps<"tbody">, "children">

const ReceiptDivider = (props: ReceiptDividerProps) => {
  const { className, classes, ...other } = props

  return (
    <tbody
      className={getClasses(classes, "divider", className)}
      {...other}
    ></tbody>
  )
}

Receipt.Divider = ReceiptDivider

const getClasses = (
  classes: Partial<typeof receiptClassNames> | undefined,
  key: keyof typeof receiptClassNames,
  ...names: unknown[]
): string => {
  const mainName = (classes && classes[key]) || receiptClassNames[key]
  const otherNames = names.filter(
    (v): v is string => !!v && typeof v == "string"
  )
  return [mainName, ...otherNames].join(" ")
}
