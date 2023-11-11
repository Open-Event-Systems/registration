import { ButtonList } from "#src/components/button-list/ButtonList"
import { InterviewOption } from "#src/features/cart/types"
import { SelfServiceRegistration } from "#src/features/selfservice/types"

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
