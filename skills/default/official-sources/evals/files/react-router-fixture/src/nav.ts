import { useHistory } from "react-router-dom";

export function useCheckoutNav() {
  const history = useHistory();
  return () => history.push("/checkout");
}
