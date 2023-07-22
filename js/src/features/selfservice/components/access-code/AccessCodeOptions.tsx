import { ButtonList } from "#src/components/button_list/ButtonList.js"
import { InterviewOption } from "#src/features/cart/types.js"
import { SelfServiceRegistration } from "#src/features/selfservice/types.js"

export type AccessCodeOptionsProps = {
  registrations: SelfServiceRegistration[]
  interviews: InterviewOption[]
  onSelectChange?: (id: string) => void
  onSelectAdd?: (id: string) => void
}

export const AccessCodeOptions = (props: AccessCodeOptionsProps) => {
  const { registrations, interviews, onSelectChange, onSelectAdd } = props

  const showDivider = registrations.length > 0 && interviews.length > 0

  return (
    <ButtonList>
      {registrations.length > 0 && (
        <>
          <ButtonList.Label>Change Registration</ButtonList.Label>
          {registrations.map((reg) => (
            <ButtonList.Button
              key={reg.id}
              onClick={() => {
                onSelectChange && onSelectChange(reg.id)
              }}
            >
              {reg.title || "Registration"}
            </ButtonList.Button>
          ))}
        </>
      )}
      {showDivider && <ButtonList.Divider />}
      {interviews.length > 0 && (
        <>
          <ButtonList.Label>New Registration</ButtonList.Label>
          {interviews.map((opt, i) => (
            <ButtonList.Button
              key={i}
              onClick={() => {
                onSelectAdd && onSelectAdd(opt.id)
              }}
            >
              {opt.name || opt.id}
            </ButtonList.Button>
          ))}
        </>
      )}
    </ButtonList>
  )
}
