

describe "Activate scripts"
	describe "General"
		describe "Env variables"
			for suffix in ROOT HOST USERSCRIPTS MOUNTS; do
				var="CLUSTER_UTILS_$suffix"
				it "Defines ${var}"
					assert present ${!var}
				end
			done
		end

		describe "Aliases"
			it "Overwrites rm correctly"
				echo $(alias rm)
				rmalias=$(alias rm)
				assert equal "${rmalias#aliasrm=}" "rm --one-file-system"
			end
		end
	end

	describe "Cli"

	end
end 
