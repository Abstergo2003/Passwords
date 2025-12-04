export function GlobalPassword(props: {
    isFirst: string,
    handleOnInput: React.FormEventHandler<HTMLInputElement>,
    passwordInputRef: React.Ref<HTMLInputElement> | undefined,
    inputPassword: React.MouseEventHandler<HTMLButtonElement>,
    passwordValid: boolean
}) {
    return(
        <div className="password">
            <h2>{props.isFirst}</h2>
            <input type="password" id="globalPassword" placeholder="Password..." onInput={props.handleOnInput} ref={props.passwordInputRef} /><br />
            <button id="globalPasswordOK" onClick={props.inputPassword} disabled={!props.passwordValid}></button><br />
            <span></span>
        </div>
    )
}