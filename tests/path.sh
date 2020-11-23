
describe "Path handling"
	describe "On activate"
		it "Defines CLUSTER_UTILS_ROOT appropiately"
			testsdir="$(dirname $(realpath "$BASH_SOURCE"))"
			assert equal "${CLUSTER_UTILS_ROOT}" "$(realpath "${testsdir}/..")"
		end
	end

	describe "clusterutils path command"
		it "Returns correct single paths"
			assert equal "$(clusterutils path test)" "${CLUSTER_UTILS_ROOT}/test"
		end

		it "Doesn't expand special characters (glob)"
			assert equal "$(clusterutils path "*")" "${CLUSTER_UTILS_ROOT}/*"
		end
	end
end
